from datetime import datetime
import pymysql
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from instagram_crawler.influencer_price_calculator import InfluencerPriceCalculator
from instagram_crawler.user_cache import UserCache
from ugly_requests import get_following

class InstagramCrawlerPipeline(object):

    DAYS = 30

    def __init__(self):
        try:
            with open('/home/omri/mysqlcreds', 'r') as f:
                passwd = f.readline().rstrip()
            port = 3306
        except:
            print 'running in local mode'
            passwd = 'root'
            port = 3307
        self.conn = pymysql.connect(host='127.0.0.1', port=port, user='root', passwd=passwd, db='influencers')
        mongo_cli = MongoClient()
        db = mongo_cli.influencers
        self.analytics_collection = db.influencer_analytics
        self.followers_by_country = {'Israel': 6000, 'USA': 100000, 'France': 20000, 'Italy': 20000}
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
        if item['followers'] > self.followers_by_country[country] and not UserCache.user_parsed(item['username'], country) and item['country'] == country:

            UserCache.set_following(item['username'], get_following(item['username'], item['user_id']), country)
            UserCache.add_to_parsed(item['username'], country)

            self._replace_into_mysql(item)
        else:
            raise DropItem

    def _process_item_update_mode(self, item):
        self._replace_into_mysql(item)
        self._update_collection(item)

    def _replace_into_mysql(self, item):
        curr = self.conn.cursor()
        media = item['media']
        del item['media']
        est_price = InfluencerPriceCalculator.calculate_price(item['followers'], item['avg_likes'])
        curr.execute("UPDATE influencers SET is_private=%s, posts=%s, username=%s, profile_picture=%s,"
                     "followers=%s, following=%s, avg_comments=%s, avg_likes=%s, user_id=%s, country=%s, est_price=%s, contact=%s WHERE user_id=%s",
                     (item['is_private'], item['posts'], item['username'], item['profile_picture'], item['followers'],
                      item['following'], item['avg_comments'], item['avg_likes'], item['user_id'], item['country'],est_price,
                      item['contact'], item['user_id']))
        # insert media into media table
        for post in media:
            curr.execute("REPLACE INTO {}({}) VALUES(%(media_id)s, %(user_id)s, %(src)s, %(likes)s, %(comments)s)"
                         .format(self.media_table, self.MEDIA_COLUMNS), post)
        self.conn.commit()

    def _update_collection(self, item):

        def prepare_analytics(item):
            # for manual runs, do not want to update mongo by mistake
            should_update = True
            influencer = self.analytics_collection.find_one({'user_id': item['user_id']})
            if influencer is not None:
                date_analytics = influencer['analytics']
                if date_analytics[-1]['date'] == str(datetime.now().date()):
                    print "Not updating, ran today already"
                    should_update = False
                elif len(date_analytics) >= self.DAYS:
                    for _ in range(date_analytics - self.DAYS):
                        date_analytics.pop(0)
            else:
                date_analytics = []

            date_analytics.append({
                "date": str(datetime.now().date()),
                "avg_comments": item['avg_comments'],
                "avg_likes": item['avg_likes'],
                "followers": item['followers'],
                "following": item['following'],
                "posts": item['posts']
            })
            return date_analytics, should_update

        analytics, should_update = prepare_analytics(item)
        key = {"user_id": item['user_id']}
        value = {"analytics": analytics, "user_id": item['user_id']}
        if should_update:
            self.analytics_collection.update(key, value, upsert=True)