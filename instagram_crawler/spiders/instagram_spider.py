import re
import json
import logging
import msgpack
import pymysql
from scrapy import Spider, Request
from instagram_crawler.custom_settings import CustomSettings
from instagram_crawler.items import InstagramProfileItems
from instagram_crawler.ugly_requests import get_following
from instagram_crawler.user_cache import UserCache

logger = logging.getLogger(__name__)

class Instagram(Spider):
    BASE_URL = "http://www.instagram.com/"
    start_urls=[]
    name='Instagram'

    def __init__(self, method='mysql', country='Israel', *a, **kw):
        super(Instagram, self).__init__(*a, **kw)
        self.method = method
        self.country = country


    def parse(self, response):
        return Instagram.parse_item(response)

    @classmethod
    def parse_item(cls, response):
        javascript = "".join(response.xpath('//script[contains(text(), "sharedData")]/text()').extract())
        json_data = json.loads("".join(re.findall(r'window._sharedData = (.*);', javascript)))

        item = InstagramProfileItems()

        data = get_extracted(json_data["entry_data"]["ProfilePage"], 0)['user']
        item['username'] = data['username']
        item['user_id'] = int(data['id'])
        item['following'] = data['follows']['count']
        item['followers'] = data['followed_by']['count']
        # change resolution url to 200x200
        item['profile_picture'] = data['profile_pic_url'].replace('150x150', '200x200')
        # TODO - resolve unicode problem (hebrew)
        #item['full_name'] = data['full_name']
        item['is_private'] = data['is_private']
        media = data['media']
        item['posts'] = media['count']
        item['avg_comments'] = cls.calc_average('comments', media, len(media['nodes']))
        item['avg_likes'] = cls.calc_average('likes', media, len(media['nodes']))
        item['country'] = cls.get_country(media)
        return item

    @classmethod
    def calc_average(cls, action, media, count):
        return reduce(lambda x,y: x + y, map(lambda post: post[action]['count'], media['nodes'])) / count

    @classmethod
    def get_country(cls, media):
        country = 'USA'
        for node in media['nodes']:
            if 'caption' in node:
                if any(u"\u0590" <= c <= u"\u05EA" for c in node['caption']):
                    country = 'Israel'
                    break

        return country

    def start_requests(self):
        if self.method == 'mysql':
            try:
                with open('/home/omri/mysqlcreds', 'r') as f:
                    passwd = f.readline().rstrip()
                conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=passwd, db='influencers')
                table = 'influencers'
                curr = conn.cursor()
                curr.execute("SELECT username FROM {}".format(table))
                res = curr.fetchall()
                for username in res:
                    yield self.make_requests_from_url(self.BASE_URL + username[0])
            except Exception as e:
                logger.error("Could not get influencers from influencers_manual db")
                logger.exception(e)
        elif self.method == 'initial':
            UserCache.set_following('chiaraferragni', get_following('neta_alchimister', '29605612'))
            UserCache.add_to_parsed('chiaraferragni')
            UserCache.set_following('songofstyle', get_following('neta_alchimister', '29605612'))
            UserCache.add_to_parsed('songofstyle')
            UserCache.set_following('garypeppergirl', get_following('neta_alchimister', '29605612'))
            UserCache.add_to_parsed('garypeppergirl')
            UserCache.set_following('weworewhat', get_following('neta_alchimister', '29605612'))
            UserCache.add_to_parsed('weworewhat')
        else:
            #generate new request for each following
            try:
                all_following = UserCache.get_all_parsed_user_following()
                for username in all_following:
                    if username:
                        yield self.make_requests_from_url(self.BASE_URL + username)
            except Exception as e:
                logger.error("Could not get influencers from redis")
                logger.exception(e)

def get_extracted(value, index):
    try:
        return value[index]
    except:
        return {}