# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class InstagramCrawlerPipeline(object):

    def __init__(self):
        passwd = ''
	with open('/home/ec2-user/mysqlcreds', 'r') as f:
            passwd = f.readline().rstrip()
        print passwd
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=passwd, db='influencers')
        self.table = 'influencers'
        self.COLUMNS = "inf_id, is_private, posts, username, profile_picture, followers, following, avg_comments, avg_likes"

    def process_item(self, item, spider):
        curr = self.conn.cursor()
        curr.execute("REPLACE INTO {}({}) VALUES(%(inf_id)s, %(is_private)s, %(posts)s, %(username)s, %(profile_picture)s,"
                     "%(followers)s, %(following)s, %(avg_comments)s, %(avg_likes)s)".format(self.table, self.COLUMNS), item.__dict__['_values'])
        self.conn.commit()
