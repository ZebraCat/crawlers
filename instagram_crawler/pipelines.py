# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exceptions import DropItem
from instagram_crawler.user_cache import UserCache
from ugly_requests import get_following

class InstagramCrawlerPipeline(object):

    def __init__(self):
        with open('/home/ec2-user/mysqlcreds', 'r') as f:
            passwd = f.readline().rstrip()
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=passwd, db='influencers')
        self.table = 'influencers'
        self.COLUMNS = "is_private, posts, username, profile_picture, followers, following, avg_comments, avg_likes, user_id"

    def process_item(self, item, spider):
        if item['followers'] > 6000 and not UserCache.user_parsed(item['username']) and item['is_from_israel']:

            UserCache.set_followers(item['username'], get_following(item['username'], item['user_id']))
            UserCache.add_to_parsed(item['username'])

            curr = self.conn.cursor()
            curr.execute("REPLACE INTO {}({}) VALUES(%(is_private)s, %(posts)s, %(username)s, %(profile_picture)s,"
                         "%(followers)s, %(following)s, %(avg_comments)s, %(avg_likes)s, %(user_id)s)"
                         .format(self.table, self.COLUMNS), item.__dict__['_values'])
            self.conn.commit()
        else:
            raise DropItem
