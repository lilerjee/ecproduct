# -*- coding: utf-8 -*-
"""
* **Market type** of vvic.com:
    #. **website** - https://www.vvic.com
    #. **city** - https://www.vvic.com/gz
    #. **mall** - https://www.vvic.com/gz/shops/19
    #. **floor** - http://www.vvic.com/hz/shops/516#1
    #. **shop** - https://www.vvic.com/shop/42780
"""
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
from ecproduct.items import ProductPage, MarketPage
from ecproduct.items import IndexPage, SearchPage, ContactPage
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose
from scrapy.http.response import urljoin
from ecproduct.spiders.ecproduct import EcproductSpider
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from urllib.request import quote
# from log import Log
import os
import sys
import re
import json
import datetime
import math
#  from debug import debugger


class VvicSpider(EcproductSpider):
    name = 'vvic'
    allowed_domains = ['vvic.com']
    # start_urls = ['http://vvic.com/']
    # handle_httpstatus_list = [301, 302]

    project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    this_file_name = os.path.basename(os.path.splitext(__file__)[0])

    custom_settings = {
        #  'FEED_URI': (
        #      'file:///' + project_path + os.path.sep +
        #      'output' + os.path.sep + this_file_name + '.jl'),
        #  'FEED_EXPORT_ENCODING': 'utf-8',
        #  'FEED_EXPORT_ENCODING': 'gb2312',
        #  'FEED_FORMAT': 'csv',
        #  'FEED_FORMAT': 'jsonlines',
        #  'FEED_EXPORT_FIELDS': ['product_color_id', 'product_color_name',
        #                         'product_id', 'product_index_img_url',
        #                         'product_source_id', 'product_link_price'],

        'LOG_ENABLED': True,
        'LOG_ENCODING': 'utf-8',
        # 'LOG_FILE': 'ecproduct.log',
        'LOG_FILE': (project_path + os.path.sep + 'log' +
                     os.path.sep + this_file_name + '.log'),
        'LOG_FORMAT': '%(asctime)s [%(name)s] %(levelname)s: %(message)s',
        'LOG_LEVEL': 'DEBUG',
        # 'LOG_LEVEL': 'INFO',
        'LOG_STDOUT': True,
    }

    platform_code = 'VVIC0'

    def __init__(self, url, entrance_page, data_type,
                 home_item_id=None, platform_code=platform_code, keyword='',
                 item_num='100', city='gz'):

        EcproductSpider.__init__(
            self, url=url, entrance_page=entrance_page,
            data_type=data_type, home_item_id=home_item_id,
            platform_code=platform_code, keyword=keyword,
            item_num=item_num, city=city)

    def start_requests(self):
        return EcproductSpider.start_requests(self)

    def parse_product_from_product_page(self, response):
        """
        Parse product detail page to get product info.
        """
        self.url = response.meta['original_url']
        loader = ItemLoader(item=ProductPage(), response=response)

        # determine if the spider is banned by website
        match_url = re.match(
            'https?://[A-Za-z0-9\-]+\.vvic\.com/item/\d+'
            '|https?://[A-Za-z0-9\-]+\.vvic\.com/item\.html?\?uuid=\d+',
            response.url)
        if not match_url:
            self.logger.warning(
                'original url: %s, response url: %s'
                % (response.meta['original_url'], response.url))
            loader.add_value('home_item_id', response.meta['home_item_id'])
            loader.add_value('url', self.url.strip())
            loader.add_value('product_id', self.url.strip(), lambda v: v[-1],
                re=r'/item/(\w+)')
            loader.add_value('product_status', 'cannot access')

            return loader.load_item()

        # plaftform info
        loader.add_value('platform_code', response.meta['platform_code'])
        loader.add_value(
            'product_category_id', response.meta.get('category_id', ''))

        # determin whether the product is deleted, or if the webpage is found
        error = response.css('div.error-main > div.error-404 > h1::text')
        if error:
            error_text = error.extract_first().strip()
            if error_text == '查找的商品已删除':
                loader.add_value('product_id', self.url.strip(),
                        Compose(lambda v: v[-1]), re='/item/(\w+)')
                loader.add_value('product_url', self.url.strip())
                loader.add_value('product_status', 'deleted')
            elif error_text == '找不到页面':
                loader.add_value('product_id', self.url.strip(),
                        Compose(lambda v: v[-1]), re='/item/(\w+)')
                loader.add_value('product_url', self.url.strip())
                loader.add_value('product_status', 'nonexistent')
            else:
                self.logger.error('other error happened: %s' % error_text)
        else:
            self._get_product_info(loader, response)
            self._get_attribute_info(loader, response)
            self._get_img_info(loader, response)
            self._get_sku_info(loader, response)
            self._get_shop_info(loader, response)

        # extra field
        loader.add_value(
            'created_time',
            datetime.datetime.strftime(datetime.datetime.today(),
                                       '%Y-%m-%d %H:%M:%S'))

        return loader.load_item()

    def _get_product_info(self, loader, response):
        # product info
        loader.add_value('product_url', self.url.strip())
        # product url '^https?://([A-Za-z0-9\-]+\.)+vvic\.com/item/(\d+)$')
        loader.add_value('product_id', self.url.strip(),
                Compose(lambda v: v[-1]), re='/item/(\w+)')
        loader.add_css(
            'product_name', 'div.product-detail div.d-name strong::text')
        loader.add_css(
            'product_sale_price',
            'div.v-price.d-p div.p-value span.fl strong.d-sale::text')
        loader.add_value('product_price_unit', 'CNY')

        loader.add_css(
            'product_source_url',
            'div.product-detail div.d-name a::attr(href)')
        loader.add_value(
            'product_source_id', response.text, re="_TID = '(\d+)';")
        loader.add_css(
            'product_source_price',
            'div.v-price > div.p-value > span.d-sale::text')
        loader.add_value('product_source_price_unit', 'CNY')

        loader.add_value(
            'product_img_index_url',
            urljoin(
                response.meta['original_url'],
                str(loader.get_value(response.text,
                    TakeFirst(), re="_INDEXIMGURL = '(.*)';"))))

        for s in response.css('div.product-detail dl.summary dd'):
            # debugger.print(s)
            if (s.css('div.name::text').extract_first() and
                    s.css('div.name::text').extract_first().strip() ==
                    '货号'):
                    loader.add_value(
                        'product_art_no',
                        s.css('div.value.ff-arial::text').extract_first(),
                        lambda v: v.strip())
            if (s.css('div.name::text').extract_first() and
                    s.css('div.name::text').extract_first().strip() == '上新时间'):
                    loader.add_value(
                        'product_upload_time',
                        s.css('div.value.ff-arial::text').extract_first(),
                        lambda v: v[0].strip(),
                        lambda v: v if len(v) >= 19 else v + ':00',
                        re='(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})')

        unshelf_time = loader.get_css(
            'div.sold-info::text', re='(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})')
        if unshelf_time:
            loader.add_value(
                'product_unshelf_time', unshelf_time,
                lambda v: v[0].strip(),
                lambda v: v if len(v) >= 19 else v + ':00')
            loader.add_value('product_status', 'unshelf')
        else:
            loader.add_value('product_status', 'onshelf')
        #  loader.add_xpath('product_unshelf_time',
        #                   '//div[@class="sold-info"]/text()',
        #                   re='(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2})')

        # get product details
        for s in response.css('div.d-attr.clearfix > ul > li'):
            loader.add_value(
                'product_detail', s.css('::text').extract(),
                lambda v: v[-1].strip().replace('\xa0', ' '))

    def _get_attribute_info(self, loader, response):
        # attribute info
        loader.add_value(
            'attr_name', response.text, re=r"_(COLOR)\s*=\s*'.*'\s*;")
        loader.add_value(
            'attr_value_id', response.text,
            lambda v: [v[-1].split(',')], re="_COLORID = '(.*)';")
        loader.add_value(
            'attr_value', response.text,
            lambda v: [v[-1].split(',')], re="_COLOR = '(.*)';")
        loader.add_value(
            'attr_name', response.text,
            re=r"_(SIZE)\s*=\s*'.*'\s*;")
        loader.add_value(
            'attr_value_id', response.text,
            lambda v: [v[-1].split(',')], re="_SIZEID = '(.*)';")
        loader.add_value(
            'attr_value', response.text,
            lambda v: [v[-1].split(',')], re="_SIZE = '(.*)';")
        #  loader.add_css(
        #      'product_upload_time',
        #      'dl.summary.clearfix dd:last-child div.value.ff-arial::text',
        #      Compose(lambda v: v[0].strip()))

    def _get_img_info(self, loader, response):
        # image info
        for s in response.css('ul#thumblist > li'):
            small_url = urljoin(
                response.meta['original_url'],
                s.css('div > a > img::attr(src)').extract_first())
            mid_url = urljoin(
                response.meta['original_url'],
                s.css('div > a > img::attr(mid)').extract_first())
            big_url = urljoin(
                response.meta['original_url'],
                s.css('div > a > img::attr(big)').extract_first())
            loader.add_value('img_url', small_url)
            loader.add_value('img_url', mid_url)
            loader.add_value('img_url', big_url)
            # for images pipeline
            # loader.add_value('image_urls', big_url)
            # https://img.alicdn.com/bao/uploaded/i4/3164746790/TB2faCjrrGYBuNjy0FoXXciBFXa_!!3164746790.jpg_60x60.jpg
            # https://img1.vvic.com/upload/1522943484301_494356.jpg?x-oss-process=image/resize,mfit,h_500,w_500
            loader.add_value('img_size', small_url, re=r'_(\d+[xX]\d+)\.')
            loader.add_value('img_size', mid_url, re=r'_(\d+[xX]\d+)\.')
            small_url_match = re.findall(r'h_(\d+),w_(\d+)', small_url)
            if small_url_match:
                loader.add_value('img_size', 'x'.join(small_url_match[0]))
            mid_url_match = re.findall(r'h_(\d+),w_(\d+)', mid_url)
            if mid_url_match:
                loader.add_value('img_size', 'x'.join(mid_url_match[0]))
            loader.add_value('img_size', '')
            # loader.add_value('status', '0')
            # loader.add_value('status', '0')
            # loader.add_value('status', '0')
            if small_url in loader.get_output_value('product_img_index_url'):
                loader.add_value('img_purpose', 'index')
            else:
                loader.add_value('img_purpose', '')
            if mid_url in loader.get_output_value('product_img_index_url'):
                loader.add_value('img_purpose', 'index')
            else:
                loader.add_value('img_purpose', '')
            if big_url in loader.get_output_value('product_img_index_url'):
                loader.add_value('img_purpose', 'index')
            else:
                loader.add_value('img_purpose', '')
            loader.add_value('img_description', 'small')
            loader.add_value('img_description', 'middle')
            loader.add_value('img_description', 'big')

    def _get_sku_info(self, loader, response):
        # get sku
        skumap = loader.get_value(
            response.text, TakeFirst(),
            lambda v: json.loads(v), re=r"_SKUMAP\s+=\s+'(.*)';")
        for sku in skumap:
            loader.add_value('sku_id', str(sku['id']))
            loader.add_value('sku_value', str(sku['skuid']))
            loader.add_value('sku_price', str(sku['discount_price']))

    def _get_shop_info(self, loader, response):
        # shop info
        loader.add_value('market_id', response.text, re="_SHOPID = '(\d+)';")
        loader.add_value('market_type', 'shop')
        loader.add_value(
            'market_url',
            urljoin(response.meta['original_url'],
                str(loader.get_css(
                    'div.stall-head.fl div[class*=stall-head-name] a::attr(href)',
                    TakeFirst()))))
        shop_loader = loader.nested_css('div.shop-info div.shop-content')
        shop_loader.add_css(
            'market_name', 'h2.shop-name span::text', lambda v: v[0].strip())

        #  shop_table = shop_loader.nested_css('ul.mt10')
        attr_list = response.css(
            'div.shop-info div.shop-content ul.mt10 div.attr::text').extract()
        value_list = response.css(
            'div.shop-info div.shop-content ul.mt10 div.text')
        if len(attr_list) != len(value_list):
            self.logger.error('shop table name and value don\'t match')
            sys.exit(1)
        if not attr_list:
            self.logger.error('shop table name list is empty')
            sys.exit(1)
        attr_list = [e.split('：')[0] for e in attr_list]

        if '排行' in attr_list:
            loader.add_value(
                'market_rank',
                value_list[attr_list.index('排行')].xpath(
                    'a/em/text()').extract())
        if '旺旺' in attr_list:
            loader.add_value(
                'market_contact_wangwang',
                value_list[attr_list.index('旺旺')].xpath(
                    'span[@class="fl"]/text()').extract())
        if '商品' in attr_list:
            # the page structure is changed
            num_class_list = value_list[attr_list.index('商品')].xpath(
                    './ol/@class').extract()
            num = ''.join(re.findall(r'v-num num(\d+)', n)[0]
                for n in num_class_list if re.findall(r'v-num num(\d+)', n))
            loader.add_value('market_item_num', num)
        if '电话' in attr_list:
            phone_class_list = value_list[attr_list.index('电话')].xpath('p')
            phones = [''.join(p.xpath('span[@class]/text()').extract())
                    for p in phone_class_list]
            loader.add_value('market_contact_phone', phones)
        if '微信' in attr_list:
            loader.add_value(
                'market_contact_weixin',
                ''.join(value_list[attr_list.index('微信')].xpath(
                    'span[@class and not(@style)]/text()').extract()))
        if 'QQ' in attr_list:
            #  loader.add_value(
            #      'market_contact_qq',
            #      value_list[attr_list.index('QQ')].xpath('text()').extract())
            loader.add_value(
                'market_contact_qq',
                ''.join(value_list[attr_list.index('QQ')].xpath(
                    'span[@class]/text()').extract()))
        if '产地' in attr_list:
            loader.add_value(
                'market_addr',
                value_list[attr_list.index('产地')].xpath('text()').extract())
        if '地址' in attr_list:
            loader.replace_value(
                'market_addr',
                loader.get_collected_values(
                    'market_addr')[0] + ' ' + value_list[
                        attr_list.index('地址')].xpath(
                            'text()').extract_first().strip())

    def parse_from_index_page(self, response):
        """
        Parse website index page to get 'city' market info.
        Indext url: http://www.vvic.com
        """
        #  if response.status in (301, 302):
        #      self.logger.error(
        #          'redirect error, status: %s' % response.status)
        #      self.logger.error(
        #          'redirect error, url: %s' % response.meta['original_url'])
        #      self.logger.error('redirect url: %s' % response.url)
        #      self.logger.error('redirect response: %s' % response.text)

        data_type = response.meta['data_type']

        if data_type in ['market', 'product']:
            original_url = response.meta['original_url']
            # get the top market info
            loader = ItemLoader(item=IndexPage(), response=response)
            top_market_num = 0
            # plaftform info
            loader.add_value('platform_code', response.meta['platform_code'])

            global_markets_str = re.findall(
                r"_gobal_marketes\s*=\s*'\[(.*)\]';", response.text)[0]
            #  global_markets = re.findall(
            #      r"{panggeFlag=(\d+),\s*code=(\w+),"
            #      "\s*rankFlag=(\d+),\s*name=(\w+),\s*id=(\d+)}",
            #      global_markets_str)
            global_markets = re.findall(
                r"panggeFlag=(\d+),\s*code=(\w+),\s*rankFlag=(\d+),"
                "\s*modelFlag=\d+,\s*name=(\w+),\s*showHot=\d+,\s*id=(\d+),",
                global_markets_str)
            next_url_list = []
            next_code_list = []
            next_addr_list = []
            next_market_id_list = []
            for market in global_markets:
                loader.add_value('market_id', market[-1])
                loader.add_value('market_name', market[-2])
                loader.add_value('market_code', market[1])
                loader.add_value('market_type', 'city')
                loader.add_value('parent_market_id', '0')
                loader.add_value(
                    'market_url', urljoin(response.meta['original_url'],
                                          market[1]))
                if market[-2] == '杭州男装':
                    loader.add_value('market_addr', '浙江省 ' + market[-2])
                else:
                    loader.add_value('market_addr', '广东 ' + market[-2])
                loader.add_value('market_status', '1')

                next_url_list.append(
                    urljoin(response.meta['original_url'], market[1]))
                next_market_id_list.append(market[-1])
                next_code_list.append(market[1])
                if market[-2] == '杭州男装':
                    next_addr_list.append('浙江省 ' + market[-2])
                else:
                    next_addr_list.append('广东 ' + market[-2])
                # next_addr_list.append('广东 ' + market[-2])
                top_market_num += 1

            loader.add_value(
                'created_time',
                datetime.datetime.strftime(datetime.datetime.today(),
                                           '%Y-%m-%d %H:%M:%S'))
            yield loader.load_item()

            # get the basic info about the website
            request = scrapy.Request(
                url=urljoin(response.request.url, '/contact.html'),
                callback=self.parse_from_contact_page)
            request.meta['original_url'] = original_url
            request.meta['platform_code'] = self.platform_code
            request.meta['market_num'] = top_market_num
            yield request

            # get city market info
            for (url, mid, code, addr) in zip(
                    next_url_list, next_market_id_list,
                    next_code_list, next_addr_list):
                self.logger.info('url, mid, code, addr:', url, mid, code, addr)

                request = scrapy.Request(
                    url=url, callback=self.parse_from_city_index_page)
                request.meta['original_url'] = url
                request.meta['platform_code'] = self.platform_code
                request.meta['market_id'] = mid
                request.meta['market_code'] = code
                request.meta['market_addr'] = addr
                request.meta['data_type'] = data_type
                yield request

    def parse_from_contact_page(self, response):
        """Get the basic info about the website"""
        #  if response.status in (301, 302):
        #      self.logger.error(
        #          'redirect error, url: %s' % response.meta['original_url'])
        #      self.logger.error('redirect response: %s' % response.text)

        loader = ItemLoader(item=ContactPage(), response=response)

        loader.add_value('platform_code', response.meta['platform_code'])
        loader.add_value('market_id', '0')
        loader.add_value('parent_market_id', '-1')
        loader.add_css(
            'market_name',
            'div.contact-left table:last-child tbody tr:first-child '
            'td:last-child::text', lambda v: v[0].strip())
        loader.add_value('market_type', 'website')
        loader.add_value('market_url', response.meta['original_url'])
        loader.add_value('market_addr',
                         '广州 天河区 元岗路 智汇Park创意园 B座505-506')
        loader.add_value('market_status', '1')
        loader.add_value('market_item_num', str(response.meta['market_num']))
        loader.add_css(
            'market_contact_mail',
            'div.contact-left table:last-child tbody tr:nth-child(2) '
            'td:last-child::text', lambda v: v[0].strip())
        loader.add_css(
            'market_contact_phone',
            'div.contact-left table:last-child tbody tr:nth-last-child(2) '
            'td:last-child::text', lambda v: v[0].strip())

        loader.add_value(
            'created_time',
            datetime.datetime.strftime(
                datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))

        return loader.load_item()

    def parse_from_city_index_page(self, response):
        """
        parse city market index page to get 'mall' market
        info(the tab '市场' in web page')

        city market index e.g.: http://www.vvic.com/gz
        """
        #  if response.status in (301, 302):
        #      self.logger.error(
        #          'redirect error, url: %s' % response.meta['original_url'])
        #      self.logger.error('redirect response: %s' % response.text)
        data_type = response.meta['data_type']

        if data_type in ['market', 'product']:
            original_url = response.meta['original_url']

            loader = ItemLoader(item=MarketPage(), response=response)
            loader.add_value('platform_code', response.meta['platform_code'])

            next_url_list = []
            next_market_id_list = []
            next_market_name_list = []
            next_code_list = []
            next_addr_list = []
            mall_market_num = 0
            for ele in response.css(
                    'div.index_markets div.index_markets_list a'):
                # 解放南鞋城 比较特殊,
                # url为http://www.vvic.com/jfn/markets.html#floor200
                if response.meta['market_code'] == 'jfn':
                    mid = response.meta['market_id'] + '-' + ele.xpath(
                        '@href').extract_first().split('#')[-1]
                    loader.add_value('market_id', mid)
                    next_market_id_list.append(mid)
                    next_code_list.append('jfn')
                else:
                    mid = ele.xpath('@href').extract_first().split('/')[-1]
                    loader.add_value('market_id', mid)
                    next_market_id_list.append(mid)
                    next_code_list.append(None)

                loader.add_value(
                    'parent_market_id', response.meta['market_id'])
                loader.add_value(
                    'market_name', ele.xpath('./text()').extract_first())
                loader.add_value('market_type', 'mall')
                loader.add_value(
                    'market_url', urljoin(
                        original_url, ele.xpath('@href').extract_first()))
                loader.add_value(
                    'market_addr',
                    response.meta['market_addr'] + ' ' + ele.xpath(
                        './text()').extract_first())
                loader.add_value('market_status', '1')

                next_url_list.append(
                    urljoin(original_url, ele.xpath('@href').extract_first()))
                next_addr_list.append(
                    response.meta['market_addr'] + ' ' + ele.xpath(
                        './text()').extract_first())
                next_market_name_list.append(
                    ele.xpath('./text()').extract_first())
                mall_market_num += 1

            loader.add_value(
                'created_time',
                datetime.datetime.strftime(
                    datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))
            yield loader.load_item()

            # update number of market mall for city market
            loader = ItemLoader(item=MarketPage(), response=response)
            loader.add_value('platform_code', response.meta['platform_code'])
            loader.add_value('market_id', response.meta['market_id'])
            loader.add_value('market_url', original_url)
            loader.add_value('market_item_num', mall_market_num)
            yield loader.load_item()

            # parse mall market index page to get 'floor' market info
            jfn_url = ''
            jfn_market_id_list = []
            for (url, mid, code, addr, name) in zip(
                    next_url_list, next_market_id_list,
                    next_code_list, next_addr_list, next_market_name_list):
                # download the web only one time for the tow urls:
                # http://www.vvic.com/jfn/markets.html#floor202
                # http://www.vvic.com/jfn/markets.html#floor201
                if code == 'jfn':
                    jfn_url = url
                    jfn_market_id_list.append(mid)
                    continue
                request = scrapy.Request(
                    url=url, callback=self.parse_from_mall_index_page)
                request.meta['original_url'] = url
                request.meta['platform_code'] = self.platform_code
                request.meta['market_id'] = mid
                request.meta['market_code'] = code
                request.meta['market_addr'] = addr
                request.meta['market_name'] = name
                request.meta['data_type'] = data_type
                yield request

            # parse mall market index page for '解放南鞋城'
            request = scrapy.Request(
                url=url, callback=self.parse_from_mall_index_page)
            request.meta['original_url'] = jfn_url.split('#')[0]
            request.meta['platform_code'] = self.platform_code
            request.meta['market_id_list'] = jfn_market_id_list
            request.meta['market_code'] = 'jfn'
            request.meta['data_type'] = data_type
            yield request

    def parse_from_mall_index_page(self, response):
        """
        parse mall market index page to get 'floor' market info and
        'shop' market info
        mall market index e.g.: http://www.vvic.com/xt/shops/400
        """
        #  if response.status in (301, 302):
        #      self.logger.error(
        #          'redirect error, url: %s' % response.meta['original_url'])
        #      self.logger.error('redirect response: %s' % response.text)

        original_url = response.meta['original_url']
        floor_market_item_num = 0
        shop_market_item_num = 0

        # get info of market floor
        loader = ItemLoader(item=MarketPage(), response=response)
        loader.add_value('platform_code', response.meta['platform_code'])

        selector_list = response.css(
            'div.w.w-shops div.mk-shops dl.stall-table')   # floor info table
        for ele in selector_list:
            data_id = ele.xpath('@data-id').extract_first()
            # 解放南鞋城 比较特殊, get shop info directly
            if response.meta['market_code'] == 'jfn':
                data_id_dict = {e.split('-')[-1]: e for e in response.meta[
                    'market_id_list']}
                # self.logger.info('**: %s' % data_id)
                if data_id in data_id_dict:
                    # update number of market shop for market mall
                    # in '解放南鞋城'
                    shop_market_item_num = ele.css(
                        '[data-id="%s"] dt span.count::text' %
                        data_id).re(r'(\d+)')[0]
                    # self.logger.info('^^: %s' % shop_market_item_num)
                    loader.add_value('market_id', data_id_dict[data_id])
                    loader.add_value('market_url', urljoin(
                        original_url, '#%s' % data_id))
                    loader.add_value('market_item_num', shop_market_item_num)
                    # yield loader.load_item()

                    # get market shop info
                    data_index = ele.xpath('./@data-index').extract_first()
                    selector_list = ele.css('dd ul.floor-item-%s li.last'
                                            % data_index)
                    yield self._parse_market_from_shop_table(
                        response, selector_list, data_id_dict[data_id])

                    # get all product in all market
                    if response.meta['data_type'] == 'product':
                        for s in selector_list:
                            url = urljoin(
                                original_url,
                                s.xpath('a/@href').extract_first())
                            request = scrapy.Request(
                                url=url, callback=(
                                    self.parse_from_market_shop_page))
                            request.meta['original_url'] = url
                            request.meta['data_type'] = response.meta[
                                'data_type']
                            request.meta['platform_code'] = self.platform_code
                            yield request
                continue

            if data_id == '-1':   # skip "推荐档口"
                continue

            if len(selector_list) == 1 and ele.xpath(
                    'dt/h2/text()').extract_first().strip() == '全部':
                shop_market_item_num = ele.css(
                    '[data-id="%s"] dt span.count::text' % data_id).re(
                        r'(\d+)')[0]
                floor_market_item_num = shop_market_item_num

                # get market shop info
                data_index = ele.xpath('./@data-index').extract_first()
                selector_list = ele.css(
                    'dd ul.floor-item-%s li.last' % data_index)
                yield self._parse_market_from_shop_table(
                    response, selector_list, response.meta['market_id'])

                break

            loader.add_value(
                'market_id', response.meta['market_id'] + '-' + data_id)
            loader.add_value('parent_market_id', response.meta['market_id'])
            loader.add_value(
                'market_name',
                response.meta['market_name'] + ' ' +
                ele.xpath('dt/h2/text()').extract_first().strip())
            loader.add_value('market_type', 'floor')
            loader.add_value(
                'market_url', urljoin(original_url, '#%s' % data_id))
            loader.add_value(
                'market_addr', response.meta['market_addr'] + ' ' +
                ele.xpath('dt/h2/text()').extract_first().strip())
            loader.add_value('market_status', '1')
            loader.add_value(
                'market_item_num',
                ele.css('dt span.count::text').extract_first(), re='(\d+)')
            floor_market_item_num += int(
                ele.css('dt span.count::text').re(r'(\d+)')[0])

            # get market shop info
            data_index = ele.xpath('./@data-index').extract_first()
            selector_list = ele.css(
                'dd ul.floor-item-%s li.last' % data_index)
            yield self._parse_market_from_shop_table(
                response, selector_list,
                response.meta['market_id'] + '-' + data_id)

            # get all product in all market
            if response.meta['data_type'] == 'product':
                for s in selector_list:
                    url = urljoin(
                        original_url, s.xpath('a/@href').extract_first())
                    request = scrapy.Request(
                        url=url,
                        callback=self.parse_from_market_shop_page)
                    request.meta['original_url'] = url
                    request.meta['data_type'] = response.meta['data_type']
                    request.meta['platform_code'] = self.platform_code
                    yield request
        else:
            loader.add_value(
                'created_time',
                datetime.datetime.strftime(
                    datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))
            yield loader.load_item()

        # update number of market floor for market mall
        # 解放南鞋城 比较特殊, get shop info directly
        if response.meta['market_code'] != 'jfn':
            loader = ItemLoader(item=MarketPage(), response=response)
            loader.add_value('platform_code', response.meta['platform_code'])
            loader.add_value('market_id', response.meta['market_id'])
            loader.add_value('market_url', original_url)
            loader.add_value('market_item_num', str(floor_market_item_num))
            loader.add_value('created_time', datetime.datetime.strftime(
                datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))
            loader.add_value('market_item_num', shop_market_item_num)
            yield loader.load_item()

    @staticmethod
    def _convert_str_to_list(comma_seperate_str, seperator='\n'):
        return seperator.join(
            e.strip() for e in comma_seperate_str.split(','))

    def _parse_market_from_shop_table(
            self, response, selector_list, market_id):
        original_url = response.meta['original_url']
        loader = ItemLoader(item=MarketPage(), response=response)
        loader.add_value('platform_code', response.meta['platform_code'])
        for s in selector_list:
            loader.add_value(
                'market_id', s.xpath('a/@data-id').extract_first())
            loader.add_value('parent_market_id', market_id)
            loader.add_value('market_type', 'shop')
            loader.add_value('market_status', '1')
            loader.add_value(
                'market_url',
                urljoin(original_url, s.xpath('a/@href').extract_first()))
            loader.add_value(
                'market_name', s.xpath('a/@data-title').extract_first())
            loader.add_value(
                'market_contact_wangwang',
                self._convert_str_to_list(
                    s.xpath('a/@data-ww').extract_first()))
            loader.add_value(
                'market_contact_qq',
                self._convert_str_to_list(
                    s.xpath('a/@data-qq').extract_first()))
            loader.add_value(
                'market_contact_phone',
                self._convert_str_to_list(
                    s.xpath('a/@data-tel').extract_first()))
            loader.add_value(
                'market_contact_weixin',
                self._convert_str_to_list(
                    s.xpath('a/@data-wachat').extract_first()))
            loader.add_value(
                'market_addr',
                (s.xpath('a/@data-source').extract_first() +
                    ' ' + s.xpath('a/@data-market').extract_first() +
                    ' ' + s.xpath('a/@data-floor').extract_first() +
                    '楼 ' + s.xpath('a/@data-position').extract_first()))
            loader.add_value(
                'market_start_time',
                datetime.datetime.strftime(datetime.datetime.strptime(
                    s.xpath('a/@data-sbd').extract_first(),
                    '%Y-%m-%d'), '%Y-%m-%d %H:%M:%S'))
            loader.add_value(
                'market_exist_time', s.xpath('a/@data-years').extract_first())

        loader.add_value(
            'created_time',
            datetime.datetime.strftime(
                datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))

        return loader.load_item()

    def parse_from_search_page(self, response):
        """
        parse search index page to get category info
        entrance url: http://www.vvic.com/gz/list/index.html
        """
        data_type = response.meta['data_type']

        if data_type == 'category':
            original_url = response.meta['original_url']
            loader = ItemLoader(item=SearchPage(), response=response)
            # plaftform info
            loader.add_value('platform_code', response.meta['platform_code'])

            # get city code
            #  global_markets_str = re.findall(
            #      r"_gobal_marketes\s*=\s*'\[(.*)\]';", response.text)[0]
            #  global_markets = re.findall(
            #      r"{panggeFlag=(\d+),\s*code=(\w+),\s*rankFlag=(\d+),"
            #      "\s*name=(\w+),\s*id=(\d+)}",
            #      global_markets_str)
            #  next_code_list = [m[1] for m in global_markets]

            # get top category code
            for s in response.css(
                    "div.search-condition div.screen "
                    "div.nav-category.nav-pid "
                    "div.nc-value div.types a[href='#']"):
                pid = s.xpath('@data-val').extract_first()
                url = urljoin(original_url, '?pid=%s' % pid)
                loader.add_value('category_id', pid)
                loader.add_value('parent_category_id', '0')
                loader.add_value(
                    'category_name',
                    s.xpath('text()').extract_first().strip())
                loader.add_value('category_url', url)
                loader.add_value('category_status', '1')
                loader.add_value('category_level', '1')
                loader.add_value('category_is_leaf', '0')

                request = scrapy.Request(
                    url=url,
                    callback=self.parse_from_search_page_with_top_category)
                request.meta['original_url'] = url
                request.meta['category_id'] = pid
                request.meta['platform_code'] = self.platform_code
                request.meta['data_type'] = data_type
                yield request

            loader.add_value(
                'created_time',
                datetime.datetime.strftime(
                    datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))
            yield loader.load_item()

        if data_type == 'product':
            keyword = response.meta['keyword']
            city = response.meta['city']
            page_num = (response.meta.get('page_num') if
                        response.meta.get('page_num', None) else '1')
            self.logger.info('keyword = %s, city = %s, page_num = %s' %
                             (keyword, city, page_num))
            url = ('https://www.vvic.com/apic/search/asy?'
                   'merge=1&q=%s&searchCity=%s&currentPage=%s' %
                   (quote(keyword), city, page_num))

            request = scrapy.Request(
                url=url,
                callback=self.parse_searched_product_from_search_ajax_page)
            request.meta['item_num'] = response.meta['item_num']
            request.meta['page_num'] = page_num
            request.meta['keyword'] = response.meta['keyword']
            request.meta['city'] = response.meta['city']
            request.meta['original_url'] = url
            request.meta['platform_code'] = self.platform_code
            yield request

    def parse_searched_product_from_search_ajax_page(self, response):
        """Parse the search page to get the product info.
        The result page not only include product, and also include shop.

        :param str keyword: The searched keyword
        :param str item_num: Number of item whick will be scraped
        """
        page_num = response.meta['page_num']
        item_num = int(response.meta['item_num'])
        self.logger.info('item_num = %s' % item_num)
        item_count = 0

        result = json.loads(response.body)

        for record in result['data']['search_page']['recordList']:
            #  self.logger.info('record:\n%s' % record)
            #  item_id = record['item_id']
            item_id = record.get('item_id', None)
            if item_id is None:     # The item is shop
                continue
            url = 'https://www.vvic.com/item/%s' % item_id
            request = scrapy.Request(url=url,
                                     callback=self.parse_product_from_product_page)
            request.meta['original_url'] = url
            request.meta['category_id'] = str(record['vcid'])
            request.meta['platform_code'] = self.platform_code
            item_count += 1
            yield request

            if item_num <= item_count:
                self.logger.info('last item_count = %s' % item_count)
                return

        self.logger.info('item_count = %s' % item_count)
        url = 'https://www.vvic.com/gz/search/index.html'
        request = scrapy.Request(
            url=url, callback=self.parse_from_search_page)
        request.meta['item_num'] = item_num - item_count
        request.meta['page_num'] = str(int(page_num) + 1)
        request.meta['data_type'] = 'product'
        request.meta['platform_code'] = self.platform_code
        request.meta['keyword'] = response.meta['keyword']
        request.meta['city'] = response.meta['city']
        yield request

    def parse_from_search_page_with_top_category(self, response):
        """
        parse top category search page to get category info
        """
        data_type = response.meta['data_type']

        if data_type == 'category':
            original_url = response.meta['original_url']
            pid = response.meta['category_id']

            loader = ItemLoader(item=SearchPage(), response=response)
            loader.add_value('platform_code', response.meta['platform_code'])

            for s in response.css('div.catid_%s > div.nav-category' % pid):

                cat_id = ''
                for s1 in s.css('div.nc-value div.types a'):
                    loader.add_value(
                        'category_name', s1.xpath('text()').extract_first())
                    loader.add_value(
                        'category_id', s1.xpath('@data-val').extract_first())
                    loader.add_value(
                        'parent_category_id',
                        s1.xpath('@data-tagid').extract_first())
                    loader.add_value(
                        'category_url',
                        original_url + '&vcid=%s' % s1.xpath(
                            '@data-val').extract_first())
                    loader.add_value('category_status', '1')
                    loader.add_value('category_level', '3')
                    loader.add_value('category_is_leaf', '1')
                    cat_id = s1.xpath('@data-tagid').extract_first()

                loader.add_value('category_id', cat_id)
                loader.add_value(
                    'category_name',
                    s.css('div.nc-key::text').extract_first())
                loader.add_value('parent_category_id', pid)
                loader.add_value('category_url', '')
                loader.add_value('category_status', '1')
                loader.add_value('category_level', '2')
                loader.add_value('category_is_leaf', '0')

            loader.add_value(
                'created_time',
                datetime.datetime.strftime(
                    datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))
            yield loader.load_item()

    def parse_from_market_shop_page(self, response):
        """
        Parse market with product page to get all product info in this market.
        Market 'shop' page: https://www.vvic.com/shop/43929
        """
        data_type = response.meta['data_type']
        if data_type == 'product':
            original_url = response.meta['original_url']

            loader = ItemLoader(item=ProductPage(), response=response)
            loader.add_value('platform_code', response.meta['platform_code'])

            # get page number for product
            #  page_num = re.findall(
            #      "window\.PAGECOUNT\s*=\s*'(\d+)'", response.text)[0]
            # get page size per page for product
            page_size = re.findall(
                "window\.PAGESIZE\s*=\s*'(\d+)'", response.text)[0]
            # get all category for product
            cat_id_list = []
            product_num_list = []
            for s in response.css(
                    'div.nav-category.show-more div.nc-value div.types a'):
                cat_id_list.append(
                    re.findall(r'\?vcid=(\d+)\&',
                               s.xpath('@href').extract_first())[0])
                product_num_list.append(
                    re.findall(r'(\d+)',
                               s.xpath('text()').extract_first())[0])

            for cat_id, product_num in zip(cat_id_list, product_num_list):
                for num in range(math.ceil(int(product_num) / int(page_size))):
                    url = original_url + '?vcid={}&currentPage={}'.format(
                        cat_id, num + 1)
                    #  self.logger.info('product_num = %s' % product_num)
                    #  self.logger.info('cat_id = %s' % cat_id)
                    #  self.logger.info('num = %s' % num)
                    #  self.logger.info('url = %s' % url)
                    #  self.logger.info('range = %s' % range(math.ceil(int(product_num) / int(page_size))))

                    request = scrapy.Request(url=url, callback=(
                        self.parse_from_market_with_product_page_pagination))
                    request.meta['original_url'] = url
                    request.meta['category_id'] = cat_id
                    request.meta['platform_code'] = self.platform_code
                    yield request

    def parse_from_market_with_product_page_pagination(self, response):
        """
        parse market with product page to get all product info in this market
        """
        original_url = response.meta['original_url']

        for s in response.css('div.goods-list.shop-list ul li'):
            url = urljoin(original_url, s.css(
                'div.item div.desc div.title a::attr(href)').extract_first())
            request = scrapy.Request(url=url,
                                     callback=self.parse_product_from_product_page)
            request.meta['original_url'] = url
            request.meta['category_id'] = response.meta['category_id']
            request.meta['platform_code'] = self.platform_code
            yield request

    def errback_parse_from_market_with_product_page(self, failure):
        # log all failures
        self.logger.error(repr(failure))

        # in case you want to do something special for some errors,
        # you may need the failure's type:

        if failure.check(HttpError):
            # these exceptions come from HttpError spider middleware
            # you can get the non-200 response
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

        elif failure.check(DNSLookupError):
            # this is the original request
            request = failure.request
            self.logger.error('DNSLookupError on %s', request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error('TimeoutError on %s', request.url)
