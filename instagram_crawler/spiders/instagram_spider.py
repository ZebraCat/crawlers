import csv
import re
import json
import logging
from scrapy import Spider
from instagram_crawler.items import InstagramProfileItems

logger = logging.getLogger(__name__)

class Instagram(Spider):
    name = "Instagram"
    start_urls = []

    download_delay = 0.5

    def parse(self, response):
        javascript = "".join(response.xpath('//script[contains(text(), "sharedData")]/text()').extract())
        json_data = json.loads("".join(re.findall(r'window._sharedData = (.*);', javascript)))

        item = InstagramProfileItems()

        data = get_extracted(json_data["entry_data"]["ProfilePage"], 0)['user']
        item['username'] = data['username']
        item['following'] = data['follows']['count']
        item['followers'] = data['followed_by']['count']
        item['profile_picture'] = data['profile_pic_url']
        # TODO - resolve unicode problem (hebrew)
        #item['full_name'] = data['full_name']
        item['is_private'] = data['is_private']
        media = data['media']
        item['posts'] = media['count']
        item['inf_id'] = media['nodes'][0]['owner']['id']
        item['avg_comments'] = self.calc_average('comments', media, len(media['nodes']))
        item['avg_likes'] = self.calc_average('likes', media, len(media['nodes']))

        return item

    def calc_average(self, action, media, count):
        return reduce(lambda x,y: x + y, map(lambda post: post[action]['count'], media['nodes'])) / count

    def start_requests(self):
        try:
            with open('instagram_crawler/data/influencers.txt', 'rb') as f:
                reader = csv.reader(f)
                for line in reader:
                    for name in line:
                        yield self.make_requests_from_url("http://www.instagram.com/" + name)
        except Exception as e:
            logger.error("Could not parse/find influencers.txt file")
            logger.exception(e)


def get_extracted(value, index):
    try:
        return value[index]
    except:
        return ""