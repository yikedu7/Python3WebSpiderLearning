# -*- coding: utf-8 -*-
import json
from scrapy import Spider, Request
from zhihuuser.items import ZhihuuserItem


class ZhihuSpider(Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    start_user = 'minmin.gong'

    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = 'allow_message%2Cis_followed%2Cis_following%2Cis_org%2Cis_blocking%2Cemployments%2Canswer_count%2Cfollower_count%2Carticles_count%2Cgender%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    follow_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follow_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    follower_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    follower_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

    def start_requests(self):
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)
        yield Request(self.follow_url.format(user=self.start_user, include=self.follow_query, offset=0, limit=20),
                      callback=self.parse_follow)
        yield Request(self.follower_url.format(user=self.start_user, include=self.follow_query, offset=0, limit=20),
                      callback=self.parse_follow)

    def requests_all(self, url_token):
        yield Request(self.user_url.format(user=url_token, include=self.user_query), callback=self.parse_user)
        yield Request(self.follow_url.format(user=url_token, include=self.follow_query, offset=0, limit=20),
                      callback=self.parse_follow)

    def parse_user(self, response):
        result = json.loads(response.text)
        item = ZhihuuserItem()
        for field in item.fields:
            if field in result.keys():
                item[field] = result[field]
        yield item

    def parse_follow(self, response):
        result = json.loads(response.text)
        if 'data' in result.keys():
            for item in result['data']:
                yield Request(self.user_url.format(user=item['url_token'], include=self.user_query), callback=self.parse_user)
                yield Request(self.follow_url.format(user=item['url_token'], include=self.follow_query, offset=0, limit=20),
                              callback=self.parse_follow)
                yield Request(
                    self.follower_url.format(user=item['url_token'], include=self.follower_query, offset=0, limit=20),
                    callback=self.parse_follow)
        if 'paging' in result.keys() and result['paging']['is_end'] == False:
            next_page = result['paging']['next']
            yield Request(next_page, callback=self.parse_follow)
