# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html


class CookiesMiddleware:

    cookies ={
        'WEIBOCN_FROM': 'deleted',
        'expires': 'Thu, 01 - Jan - 1970 00: 00:01 GMT',
        'path': '/',
        'domain': '.weibo.cn'
    }

    def process_request(self, request, spider):
        request.cookies = self.cookies
