import re
import json

from scrapy import Spider
from instagram_crawler.items import InstagramProfileItems


class Instagram(Spider):
    name = "Instagram"
    start_urls = ["http://instagram.com/nike/"]

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
        item['full_name'] = data['full_name']
        item['is_private'] = data['is_private']
        media = data['media']
        item['posts'] = media['count']
        item['inf_id'] = media['nodes'][0]['owner']['id']
        item['avg_comments'] = self.calc_average('comments', media, len(media['nodes']))
        item['avg_likes'] = self.calc_average('likes', media, len(media['nodes']))

        return item

    def calc_average(self, action, media, count):
        return reduce(lambda x,y: x + y, map(lambda post: post[action]['count'], media['nodes'])) / count


def get_extracted(value, index):
    try:
        return value[index]
    except:
        return ""