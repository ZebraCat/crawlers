import pymysql
from scrapy.exceptions import DropItem
from instagram_crawler.user_cache import UserCache
from ugly_requests import get_following

class InstagramCrawlerPipeline(object):

    def __init__(self):
        with open('/home/omri/mysqlcreds', 'r') as f:
            passwd = f.readline().rstrip()
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=passwd, db='influencers')
        self.followers_by_country = {'Israel': 6000, 'USA': 100000}
        self.influencer_table = 'influencers'
        self.INFLUENCER_COLUMNS = "is_private, posts, username, profile_picture, followers, following, avg_comments, avg_likes, user_id, country"
        self.media_table = 'media'
        self.MEDIA_COLUMNS = "media_id, user_id, src, likes, comments"

    def process_item(self, item, spider):
        if spider.method == 'mysql':
            self._process_item_update_mode(item)
        else:
            self._process_item_scrape_mode(item, spider.country)


    def _process_item_scrape_mode(self, item, country):
        if item['followers'] > self.followers_by_country[country] and not UserCache.user_parsed(item['username']) and item['country'] == country:

            UserCache.set_following(item['username'], get_following(item['username'], item['user_id']))
            UserCache.add_to_parsed(item['username'])

            self._replace_into_mysql(item)
        else:
            raise DropItem

    def _process_item_update_mode(self, item):
        self._replace_into_mysql(item)

    def _replace_into_mysql(self, item):
        curr = self.conn.cursor()
        media = item['media']
        del item['media']
        curr.execute("REPLACE INTO {}({}) VALUES(%(is_private)s, %(posts)s, %(username)s, %(profile_picture)s,"
                     "%(followers)s, %(following)s, %(avg_comments)s, %(avg_likes)s, %(user_id)s, %(country)s)"
                     .format(self.influencer_table, self.INFLUENCER_COLUMNS), item.__dict__['_values'])
        # insert media into media table
        for post in media:
            curr.execute("REPLACE INTO {}({}) VALUES(%(media_id)s, %(user_id)s, %(src)s, %(likes)s, %(comments)s)"
                         .format(self.media_table, self.MEDIA_COLUMNS), post)
        self.conn.commit()