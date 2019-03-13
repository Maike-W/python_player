# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import random




class UserAgentDownloadMiddleware(object):
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'Mozilla/5.0 (Macintosh; PPC Mac OS X 10_5_8) AppleWebKit/537.3+ (KHTML, like Gecko) iCab/5.0 Safari/533.16',
        'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)',
        'Mozilla/5.0 (compatible; U; ABrowse 0.6; Syllable) AppleWebKit/420+ (KHTML, like Gecko)',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; Avant Browser; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)',
        'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en; rv:1.9.0.18) Gecko/2010021619 Camino/2.0.2 (like Firefox/3.0.18)',
    ]
    def process_request(self, request, spider):
        user_gent=random.choice(self.USER_AGENTS)
        print(user_gent)
        request.headers['User-Agent']=user_gent
