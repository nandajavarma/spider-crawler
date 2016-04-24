#!/usr/bin/python
# -*- coding: utf-8 -*-

import scrapy, re
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
        item["title"] = response.xpath('//div[contains(@id, "CatalogEntryViewDetails_productInfo")]/div[@class="product_name"]/text()').extract_first().encode('utf-8').strip('\t\n\r \"\'')
        model = response.xpath("//div[starts-with(@id, 'CatalogEntryViewDetails_productInfo')]/p[@class='model']/text()").extract()
        item["model"] = re.sub("Model: ", '', model[0])
        item["specs"] = self.get_spec_values(response)
        item["upc"] = ''
        if item["specs"]:
            for ele in item["specs"]:
                if ele['name'] == 'Product UPC':
                    item["upc"] = ele['value']
                elif ele['name'] == 'Manufacturer Model Number':
                    item["mpn"] = ele['value']
                else:
                    continue
        item["trail"] = response.xpath('//div[@id="widget_breadcrumb"]/ul/li/a/text()').extract()
        item["currency"] =  response.css('#currentOrderCurrency::attr(value)').extract()
        online_only =  response.css('.online_only_text_reviews::text').extract()
        item["available_instore"] = False if online_only else True
        instore_only =  response.xpath('//input[starts-with(@id, "inStoreOnly")]/@value').extract()
        item["available_online"] = False if instore_only else True
        desc = response.css('.productDescHeaderList p::text').extract()
        item["description"] = self.format_list_vals(desc)
        features = response.xpath('//span[starts-with(@id, "descAttributeValue")]/text()').extract()
        item["features"] = self.format_list_vals(features)


        productinfo = self.get_data_from_js(response)
        if productinfo:
            item = self.get_data_from_product_info(item, productinfo)
        yield item

    def get_data_from_product_info(self, item, productinfo):
        item["brand"] = productinfo.get("brand")
        item["current_price"] = float(productinfo.get("offer_price"))
        item["original_price"] = float(productinfo.get("base_price"))
        item["retailer_id"] = productinfo.get("catentryid")
        item["sku"] = productinfo.get("sku")
        val =  float(productinfo.get("review_stars"))
        item["rating"] = str(val/5*100)
        for key, val in productinfo.iteritems():
            if "thumbnailURL" in key:
                image = key.split(' ')[0].strip("\"\'")
                item["primary_image_url"] = re.sub("\?.*$", '', image)
                break
        return item


    def format_list_vals(self, val):
        return filter(None, map(lambda x: x.strip("\n\r\t \"\'"), val))

    def get_data_from_js(self, response):
        productinfo = response.xpath("//body").re(r'atd.addProduct\(([\w*\W*\s*\n*]*?)\)\;')
        if not productinfo:
            return None
        productinfo = map(lambda x: x.strip(' \t\r\n\*\/'), productinfo[0].split('\n'))
        data = {}
        for info in filter(None, productinfo):
            v = info.split(',')
            data[v[-1].encode('utf-8').strip(' \/\*')] = v[0].encode('utf-8').strip('\"\'')
        return data

    def get_spec_values(self, response):
        speclist = []
        for each in response.css('.specDetails'):
            names = each.css('.specdesc span::text').extract()
            values = each.css('.specdesc_right::text').extract()
            for n, v in zip(names, values):
                specs = {}
                specs["name"] = n.encode('utf-8').strip('\t\n\r:\"\' ')
                specs["value"] = v.encode('utf-8').strip('\t\n\r:\"\' ')
                speclist.append(specs)
        return speclist
