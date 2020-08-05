# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
from ecproduct.items import ProductPage
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
from scrapy.http.response import urljoin
# from log import Log
import os, sys
import re


class WsySpider(scrapy.Spider):
    name = 'wsy'
    allowed_domains = ['wsy.com']
    # start_urls = ['http://wsy.com/']

    def __init__(self, url, home_item_id=None):

        if isinstance(url, list):
            self.url_list = url
        else:
            self.url_list = [url]

        if home_item_id is not None:
            if isinstance(home_item_id, list):
                self.home_item_id_list = home_item_id
            else:
                self.home_item_id_list = [home_item_id]

            if len(self.url_list) != len(self.home_item_id_list):
                self.logger.error('The length of url_list is not equal to the'
                        'length of home_item_id_list')
        else:
            self.home_item_id_list = []

    def start_requests(self):

        for url in self.url_list:
            # self.url = url
            request = scrapy.Request(url=url, callback=self.parse_product)

            request.meta['original_url'] = url
            if self.home_item_id_list:
                request.meta['home_item_id'] = self.home_item_id_list[
                        self.url_list.index(url)]
            else:
                request.meta['home_item_id'] = None

            print('grab: %s' % url)
            yield request

    def parse_product(self, response):
        """
        parse product detail page
        """
        self.url = response.meta['original_url']
        loader = ItemLoader(item=ProductPage(), response=response)
        # determine if the spider is banned by website
        match_url = re.match(
                r'https?://[a-zA-Z0-9\-]+\.wsy\.com/item\.html?\?id=\d+',
                response.url)
        if not match_url:
        # if response.status >= 300 and response.status < 400:    # 3xx Redirection
            self.logger.warn(
                    'original url: %s, response url: %s' % (
                        response.meta['original_url'], response.url))
            loader.add_value('home_item_id', response.meta['home_item_id'])
            loader.add_value('url', self.url.strip())
            loader.add_value('product_id', self.url.strip(),
                    lambda v: v[-1], re=r'\?id=(\d+)')
            loader.add_value('product_status', response.url)
            return loader.load_item()

        # product info
        loader.add_value('home_item_id', response.meta['home_item_id'])
        loader.add_value('product_url', self.url.strip())
       # product url ''https?://item\.jd\.com/\d+\.html?'
        loader.add_value('product_id', self.url.strip(),
                lambda v: v[-1], re=r'\?id=(\d+)')
        loader.add_css('product_status', 'div.item-dizhi-xiajia h3::text')
        loader.add_css('product_upload_time',
                'div.item-msg-time span::text', re=r'(\d+-\d+-\d+)')

        return loader.load_item()

