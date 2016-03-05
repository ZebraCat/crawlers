# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field

class InstagramProfileItems(Item):
    is_private = Field()
    posts = Field()
    username = Field()
    profile_picture = Field()
    # TODO - resolve unicode error (Hebrew)
    #full_name = Field()
    followers = Field()
    following = Field()
    avg_comments = Field()
    avg_likes = Field()
