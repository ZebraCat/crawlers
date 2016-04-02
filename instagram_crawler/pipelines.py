# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import redis
from ugly_requests import get_following

class InstagramCrawlerPipeline(object):

    def __init__(self):
        passwd = ''
        with open('/home/ec2-user/mysqlcreds', 'r') as f:
            passwd = f.readline().rstrip()
        print passwd
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=passwd, db='influencers')
        self.table = 'influencers'
        self.COLUMNS = "is_private, posts, username, profile_picture, followers, following, avg_comments, avg_likes, user_id"
        self.redis_conn = redis.StrictRedis() #TODO set passwords, logical db and such

    def process_item(self, item, spider):
        if item.followers > 6000 and self.redis_conn.get(item.username) is None:
            self.redis_conn.lset(item.username, get_following(item.username, item.user_id))
            curr = self.conn.cursor()
            curr.execute("REPLACE INTO {}({}) VALUES(%(is_private)s, %(posts)s, %(username)s, %(profile_picture)s,"
                         "%(followers)s, %(following)s, %(avg_comments)s, %(avg_likes)s, %(user_id)s)"
                         .format(self.table, self.COLUMNS), item.__dict__['_values'])
            self.conn.commit()