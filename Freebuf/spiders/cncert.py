# -*- coding: utf-8 -*-
import time

import scrapy
from scrapy.http import Request

from ..items import ArticleItem


class CncertSpider(scrapy.Spider):
    name = 'cncert'
    allowed_domains = ['www.cert.org.cn']
    start_urls = ['http://cert.org.cn/']
    baseUrl = 'http://www.cert.org.cn'

    def start_requests(self):
        yield Request('http://www.cert.org.cn/publish/main/9/index.html', self.parseBugNotice)
        yield Request('http://www.cert.org.cn/publish/main/17/index.html', self.parseSecureReport)

    def parseBugNotice(self, response):
        lis = response.css('ul.waring_con li')
        article = ArticleItem()
        for li in lis:
            article['title'] = li.css('a::text').extract_first().strip()
            article['url'] = self.baseUrl + li.css('a::attr(onclick)').extract_first().split('"')[-2]
            timeString = li.css('span::text').extract_first().strip()[1:-1]
            article['date'] = int(time.mktime(time.strptime(timeString, '%Y-%m-%d')))
            article['author'] = '国家互联网应急中心'
            article['catid'] = 1
            article['source'] = 'CNCERT'
            yield article

    def parseSecureReport(self, response):
        lis = response.css('ul.waring_con li')
        for li in lis:
            downloadPage = self.baseUrl + li.css('a.newslist_style::attr(href)').extract_first()
            yield Request(downloadPage, self.parseDownloadLink)

    def parseDownloadLink(self, response):
        article = ArticleItem()
        item = response.css('div.artil_content font a')
        if len(item) != 0:  # 网络安全信息与动态周报
            article['title'] = item[0].css('::text').extract_first()
        elif len(response.css('div.artil_content a font')) != 0:  # 国家信息安全漏洞共享平台(CNVD)周报
            item = response.css('div.artil_content a')
            article['title'] = item[0].css('font::text').extract_first().strip()
        else:  # CNCERT互联网安全威胁报告
            item = response.css('div.artil_content a')
            article['title'] = item[0].css('::text').extract_first().strip()
        article['url'] = self.baseUrl + item[0].css('::attr(href)').extract_first()
        timeString = response.css('div.artil_art::text').extract_first().strip()[-10:]
        article['date'] = int(time.mktime(time.strptime(timeString, '%Y-%m-%d')))
        article['author'] = '国家互联网应急中心'
        article['source'] = 'CNCERT'
        article['catid'] = 2
        article['url'] = self.baseUrl + item[0].css('::attr(href)').extract_first()
        yield article
