# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.cn']
    search_url = 'https://weibo.cn/search/mblog?'
    max_page = 100

    def start_requests(self):
        keyword = '110'
        for page in range(self.max_page):
            data = {
                'hideSearchFrame': '',
                'keyword': keyword,
                'page': str(page),
            }
            yield FormRequest(url=self.search_url, formdata=data, callback=self.parse)

    def parse(self, response):
        print(response.text)
