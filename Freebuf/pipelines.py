# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql

from .items import ArticleItem


class MysqlPipeline(object):
    def __init__(self, host, db, port, user, password, table):
        self.host = host
        self.db = db
        self.port = port
        self.user = user
        self.password = password
        self.table = table

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            db=crawler.settings.get('MYSQL_DB'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            table=crawler.settings.get('MYSQL_TABLE')
        )

    def open_spider(self, spider):
        self.connection = pymysql.connect(self.host, self.user, self.password, self.db, charset='utf8')
        self.cursor = self.connection.cursor()

    def close_spider(self, spider):
        self.connection.close()

    def process_item(self, item, spider):
        if isinstance(item, ArticleItem):
            # 过滤掉招聘、活动等文章
            filterContent = ['freebuf.com/jobs', 'freebuf.com/fevents']
            for keyword in filterContent:
                if keyword in item['url']:
                    return None

            self.cursor.execute('select url from ' + self.table + ' where url=%s', (item['url']))
            if self.cursor.rowcount > 0:
                # print('已存在')
                return None
            data = dict(item)
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = ('insert into ' + self.table + ' ( {} ) values({})').format(keys, values)
            self.cursor.execute(sql, tuple(data.values()))
            self.connection.commit()
            return item
