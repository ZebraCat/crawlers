import re
import json
import logging
import pymysql
from langid.langid import LanguageIdentifier, model
from scrapy import Spider
from instagram_crawler.items import InstagramProfileItems
from instagram_crawler.user_cache import UserCache


logger = logging.getLogger(__name__)

class Instagram(Spider):
    BASE_URL = "http://www.instagram.com/"
    EMAIL_REGEX = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))

    start_urls=[]
    name='Instagram'
    _identifier = None


    def __init__(self, method='mysql', country='Israel', *a, **kw):
        super(Instagram, self).__init__(*a, **kw)
        self.method = method
        self.country = country
        self.manual_run_names = ['marianodivaio', 'chiaraferragni', 'melissasatta', 'chiarabiasi', 'paolamod_lc']


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
        item['media'] = cls.get_media(media)
        item['country'] = cls.get_country(media)
        item['contact'] = cls.get_contact(data['biography']) if data['biography'] else None
        return item

    @classmethod
    def get_media(cls, media):
        user_media = []
        for post in media['nodes']:
            if not post['is_video']:
                curr = {}
                curr['media_id'] = post['id']
                curr['user_id'] = post['owner']['id']
                if re.search(r"([0-9]{3}x[0-9]{3})", post['display_src']):
                    curr['src'] = re.sub(r"([0-9]{3}x[0-9]{3})", '200x200', post['display_src'])
                else:
                    split_url = post['display_src'].split('t51.2885-15')
                    if len(split_url) == 2:
                        curr['src'] = split_url[0] + 't51.2885-15/s200x200' + split_url[1]
                    else:
                         continue
                curr['likes'] = post['likes']['count']
                curr['comments'] = post['comments']['count']
                user_media.append(curr)
        return user_media

    @classmethod
    def calc_average(cls, action, media, count):
        return reduce(lambda x,y: x + y, map(lambda post: post[action]['count'], media['nodes'])) / count

    @classmethod
    def get_country(cls, media):
        country = 'USA'
        for node in media['nodes']:
            if 'caption' in node:
                if cls.is_hebrew_string(node['caption']):
                    country = 'Israel'
                    break

                res = cls.get_identifier().classify(node['caption'])
                proba = res[1]
                lang = res[0]
                if lang == 'fr' and proba > 0.8:
                    country = 'France'
                    break
                elif lang == 'it' and proba > 0.8:
                    country = 'Italy'
                    break

        return country

    @classmethod
    def get_identifier(cls):
        if cls._identifier is None:
            cls._identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        return cls._identifier

    @classmethod
    def is_hebrew_string(cls, string):
        return any(u"\u0590" <= c <= u"\u05EA" for c in string)

    @classmethod
    def get_contact(cls, bio):
        result = re.search(cls.EMAIL_REGEX, bio)
        return None if result is None else result.group()


    def start_requests(self):
        if self.method == 'mysql':
            try:
                try:
                    with open('/home/omri/mysqlcreds', 'r') as f:
                        passwd = f.readline().rstrip()
                    port = 3306
                except:
                    print 'running in local mode'
                    passwd = 'root'
                    port = 3307
                conn = pymysql.connect(host='127.0.0.1', port=port, user='root', passwd=passwd, db='influencers')
                table = 'influencers'
                curr = conn.cursor()
                curr.execute("SELECT username FROM {}".format(table))
                res = curr.fetchall()
                blacklist = UserCache.get_black_list()
                for username in res:
                    if username not in blacklist:
                        yield self.make_requests_from_url(self.BASE_URL + username[0])
            except Exception as e:
                logger.error("Could not get influencers from influencers_manual db")
                logger.exception(e)

        elif self.method == 'manual':
            for username in self.manual_run_names:
                yield self.make_requests_from_url(self.BASE_URL + username)
        else:
            #generate new request for each following
            try:
                all_following = UserCache.get_all_parsed_user_following(self.country)
                blacklist = UserCache.get_black_list()
                for username in all_following:
                    if username and username not in blacklist:
                        yield self.make_requests_from_url(self.BASE_URL + username)
            except Exception as e:
                logger.error("Could not get influencers from redis")
                logger.exception(e)

def get_extracted(value, index):
    try:
        return value[index]
    except:
        return {}