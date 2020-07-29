# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
#  import random
#  import base64
#  from ecproduct.items import ProductPage
#  from scrapy.loader import ItemLoader
#  from scrapy.loader.processors import TakeFirst, Compose
#  from scrapy.http.response import urljoin
# from log import Log
#  import os, sys
#  import re
#  import json


class EcproductSpider(scrapy.Spider):
    # name = 'vvic'
    # allowed_domains = ['vvic.com']
    # start_urls = ['http://vvic.com/']

    def __init__(self, url, entrance_page, data_type,
                 home_item_id=None, platform_code=None, keyword='',
                 item_num='100', city='gz'):
        """
        url is str or list, accordingly home_item_id is str or list.

        entrance_page:
            The entrance which spider is in(this is relative with url)

        data_type:
            The last infomation type which is will be gotten.
            product, market, category, etc.
        """

        if isinstance(url, list):
            self.url_list = url
        elif isinstance(url, str):
            self.url_list = [url]
        else:
            self.logger.error(
                'url is not str or list, please input correct url')

        if home_item_id:
            if isinstance(home_item_id, list):
                self.home_item_id_list = home_item_id
            elif isinstance(home_item_id, str):
                self.home_item_id_list = [home_item_id]
            else:
                self.logger.error(
                    'home_item_id is not str or list,'
                    'please input correct home_item_id')

            if len(self.url_list) != len(self.home_item_id_list):
                self.logger.error(
                    'The length of url_list is not equal'
                    'to the length of home_item_id_list')
        else:
            self.home_item_id_list = []

        self.platform_code = platform_code
        self.entrance_page = entrance_page
        self.data_type = data_type
        self.keyword = keyword
        self.item_num = item_num
        self.city = city

    def start_requests(self, **kargs):
        """
        data_type:
            product, category, market.

        """
        for url in self.url_list:
            if self.entrance_page == 'product':
                request = scrapy.Request(
                    url=url, callback=self.parse_product_from_product_page,
                    **kargs)
            if self.entrance_page == 'index':
                request = scrapy.Request(
                    url=url, callback=self.parse_from_index_page)
            if self.entrance_page == 'search':
                request = scrapy.Request(
                    url=url, callback=self.parse_from_search_page)
            if self.entrance_page == 'market':
                request = scrapy.Request(
                    url=url, callback=self.parse_from_market_shop_page,
                    errback=self.errback_parse_from_market_with_product_page)
            if self.entrance_page == 'category':
                request = scrapy.Request(
                    url=url, callback=self.parse_from_category_page)

            request.meta['original_url'] = url
            request.meta['platform_code'] = self.platform_code
            request.meta['data_type'] = self.data_type
            request.meta['keyword'] = self.keyword
            request.meta['item_num'] = self.item_num
            request.meta['city'] = self.city

            #  username = 'lum-customer-lightinthebox-zone-gen'
            #  password = '8a50b61fb090'
            #  port = 22225
            #  session_id = random.random()
            #  super_proxy_url = (
            #      'http://%s-country-cn-session-%s:%s@zproxy.luminati.io:%d' %
            #      (username, session_id, password, port))
            #  request.meta['proxy'] = super_proxy_url
            #  #  request.meta['ssl'] = super_proxy_url
            #
            #  # Use the following lines if your proxy requires authentication
            #  proxy_user_pass = "lum-customer-lightinthebox-zone-gen:8a50b61fb090"
            #  # setup basic authentication for the proxy
            #  encoded_user_pass = base64.encodebytes(
            #      proxy_user_pass.encode('utf-8'))
            #  request.headers['Proxy-Authorization'] = (
            #      'Basic ' + encoded_user_pass.decode('utf-8').strip())
            #  request.headers['X-Forwarded-For'] = '202.34.43.12'

            #  request.meta['proxy'] = 'http://127.0.0.1:8087'

            if self.home_item_id_list:
                request.meta['home_item_id'] = self.home_item_id_list[
                    self.url_list.index(url)]
            else:
                request.meta['home_item_id'] = None

            print('grab: %s' % url)
            yield request
