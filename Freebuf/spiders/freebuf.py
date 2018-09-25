# -*- coding: utf-8 -*-
import time

import scrapy
from bs4 import BeautifulSoup

from ..items import ArticleItem


class FreebufSpider(scrapy.Spider):
    name = 'freebuf'
    allowed_domains = ['www.freebuf.com']
    start_urls = ['http://www.freebuf.com/']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'Freebuf.middlewares.SeleniumMiddleware': 300,
        },
    }

    def parse(self, response):
        article = ArticleItem()
        page = BeautifulSoup(response.text, 'lxml')
        news_group = page.select('div.news-info')
        for item in news_group:
            article['title'] = item.select_one('dl dt a').text.strip()
            article['url'] = item.select_one('dl dt a')['href']
            article['date'] = int(
                time.mktime(time.strptime(item.select_one('span.time').text.strip(), '%Y-%m-%d')))
            article['author'] = item.select_one('a[rel="author"]').text.strip()
            article['catid'] = self.typeMap(article['url'])
            article['source'] = 'Freebuf'
            yield article

    def typeMap(self, url):
        # 根据 URL 来确定对应的分类 id
        maps = {
            'vuls': 1,
            'sectool': 3,
            'articles/web': 4,
            'articles/system': 4,
            'articles/network': 4,
            'articles/wireless': 4,
            'articles/terminal': 4,
            'articles/database': 4,
            'articles/neopoints': 6,
            'articles/security-management': 5,
            'articles/es': 5,
            'ics-articles': 4,
            'articles/paper': 2,
            'news': 6,
        }
        for key in maps:
            if key in url:
                return maps[key]
        return 99999  # 表示不存在
