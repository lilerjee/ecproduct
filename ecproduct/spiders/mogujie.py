# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
from ecproduct.items import ProductPage, MarketPage, IndexPage, SearchPage, ContactPage
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
from scrapy.http.response import urljoin
from ecproduct.spiders.ecproduct import EcproductSpider
# from log import Log
import os, sys
import re
import json
import datetime
#  from debug import debugger


class MogujieSpider(scrapy.Spider):
    name = 'mogujie'
    allowed_domains = ['mogujie.com']
    start_urls = ['http://mogujie.com/']

    project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    this_file_name = os.path.basename(os.path.splitext(__file__)[0])

    custom_settings = {
        # 'FEED_URI': 'file:///' + project_path +  os.path.sep + 'output' + os.path.sep + this_file_name + '.jl',
        # 'FEED_EXPORT_ENCODING': 'utf-8',
        # 'FEED_EXPORT_ENCODING': 'gb2312',
        # 'FEED_FORMAT': 'csv',
        # 'FEED_FORMAT': 'jsonlines',
        # 'FEED_EXPORT_FIELDS': ['product_color_id','product_color_name','product_id','product_index_img_url','product_source_id','product_link_price'],

        'LOG_ENABLED': True,
        'LOG_ENCODING': 'utf-8',
        # 'LOG_FILE': 'ecproduct.log',
        'LOG_FILE': project_path + os.path.sep + 'log' + os.path.sep + this_file_name + '.log',
        'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        'LOG_LEVEL': 'DEBUG',
        # 'LOG_LEVEL': 'INFO',
        'LOG_STDOUT': True,
        }

    platform_code = 'VVIC0'

    def __init__(self, url, entrance_page, data_type, home_item_id=None, platform_code=platform_code):
        EcproductSpider.__init__(self, url=url, entrance_page=entrance_page, data_type=data_type, home_item_id=home_item_id, platform_code=platform_code)

    def start_requests(self):
        return EcproductSpider.start_requests(self)
    def parse(self, response):
        pass
