#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from trialcrawl.items import TrialcrawlItem

class TrialSpider(Spider):
    name = "trial"
    allowed_domains = ["hhgregg.com"]
    start_urls = ["http://www.hhgregg.com/shop-all-categories"]

    def parse(self, response):
        for sel in response.css("ul > li.subcategory > a::attr('href')"):
            url = response.urljoin(sel.extract())
            yield scrapy.Request(url, callback=self.parse_dir_contents)

    def parse_dir_contents(self, response):
        urls = response.css(".product_name a::attr(href)")
        for url in urls:
            product = response.urljoin(url.extract())
            yield scrapy.Request(product, callback=self.parse_product_items)

    def parse_product_items(self, response):
        item = TrialcrawlItem()
        item["url"] = response.url
        yield item
