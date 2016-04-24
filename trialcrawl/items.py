# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TrialcrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    currency = scrapy.Field()
    current_price = scrapy.Field()
    original_price = scrapy.Field()
    description = scrapy.Field()
    brand = scrapy.Field()
    title = scrapy.Field()
    retailer_id = scrapy.Field()
    model = scrapy.Field()
    mpn = scrapy.Field()
    sku = scrapy.Field()
    upc = scrapy.Field()
    image_urls = scrapy.Field()
    primary_image_url = scrapy.Field()
    features = scrapy.Field()
    specs = scrapy.Field()
    trail = scrapy.Field()
    rating = scrapy.Field()
    available_instore = scrapy.Field()
    available_online = scrapy.Field()
