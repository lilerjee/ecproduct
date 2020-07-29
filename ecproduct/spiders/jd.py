# -*- coding: utf-8 -*-
r"""
* Commands to run jd Spider:

  #. Add right URLs to `input/jd_url_test.txt` or `input/jd_url.txt`.
  #. Run the following commands.

     * Get all products info from search page according to one keyword::

        $ scrapy crawl jd -a url=https://www.jd.com/allSort.aspx -a entrance_page=category -a data_type=category -o output/jd.jl

        $ python main.py jd search product -f test -a keyword=空调

        $ python main.py jd search product -f test -a keyword=空调 -a item_num=80
"""
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
from ecproduct.items import ProductPage, CategoryPage
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Compose, MapCompose
from scrapy.http.response import urljoin
from ecproduct.spiders.ecproduct import EcproductSpider
# from log import Log
import os
#  import sys
import re
import json
import requests
import datetime
from urllib.parse import unquote, quote
#  from debug import debugger


class JdSpider(EcproductSpider):
    name = 'jd'
    #  allowed_domains = ['jd.com']
    # start_urls = ['http://jd.com/']
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
        #  'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    platform_code = 'JD000'

    def __init__(self, url, entrance_page, data_type,
                 home_item_id=None, platform_code=platform_code, keyword='',
                 item_num='100', city='gz'):

        EcproductSpider.__init__(
            self, url=url, entrance_page=entrance_page,
            data_type=data_type, home_item_id=home_item_id,
            platform_code=platform_code, keyword=keyword,
            item_num=item_num, city=city)

    def start_requests(self):
        return EcproductSpider.start_requests(self, dont_filter=True)

    def parse_product_from_product_page(self, response):
        """
        Parse product detail page to get product info.
        """
        #  self.url = response.meta['original_url']
        loader = ItemLoader(item=ProductPage(), response=response)

        # determine if the spider is banned by website
        match_url = re.match(r'https?://item\.jd\.com/\d+\.html?|'
                             r'https?://item\.jd\.hk/\d+\.html?',
                             response.url)
        if not match_url:
            self.logger.info('original url: %s, response url: %s' %
                             (response.meta['original_url'], response.url))
            loader.add_value('platform_code', response.meta['platform_code'])
            loader.add_value('home_item_id', response.meta['home_item_id'])
            loader.add_value('product_url', self.url.strip())
            loader.add_value('product_id', self.url.strip(),
                             lambda v: v[-1], re=r'(\d+)')
            loader.add_value('product_status', 'cannot access')
            loader.add_value(
                'created_time',
                datetime.datetime.strftime(
                    datetime.datetime.today(), '%Y-%m-%d %H:%M:%S')
            )

            return loader.load_item()
        else:
            # The request url may be as bellows:
            # https://ccc-x.jd.com/dsp/nc?ext=aHR0cHM6Ly9pdGVtLmpkLmNvbS80OTM5ODMxLmh0bWw&log=q1Yj9nGj0az5p_f3GpjDWo1DlVIyr44lyYMx6sqGtRNYFx2H2LfXMu-oEefR4l7hZk5eJkqmy8PwUi9IE7ok6elKFZWr-tsOzfCCfa9dMEqRorhwFGydKlO27eBZz7q6bUkA2ZFWq37FDi9bUbaBfNJu10hdEyGh5fQT1WoXPjyzIkV3_wjZu5RVzsSXEQl0p-dEIcjk6wDuDT93xMgqXV62hGxcs1WJxVceTfNytTy4jXPSCGtgK1FAeNFZHt6IXBqbJ4swaPP6LvgCmzkUfhqvtUdeeifwr0GhoYAGRhnK89h6fjUaIKP71FToWAFzRozgXujcWKCfuj7VBuWP2IQgRxcxw_sAjtLF4knonk8PFD7xnBgNMoHOy1slvxDsA7E0Vi3dMkV3A2zzNk15x9BZMf25OSsbbaWnoq3wBtp4kNSLxTBoFTPn9d-6CjsE&v=404
            # but the response url may be normal, as bellows:
            # https://item.jd.com/4939831.html?jd_pop=fcb08a95-96f5-4787-8e4d-c8b007821cf3&abt=0
            self.url = match_url.group()

        # plaftform info
        loader.add_value('platform_code', response.meta['platform_code'])

        loader.add_value('product_category_id',
                         response.meta.get('category_id', None))

        self._get_product_info(loader, response)
        self._get_attribute_sku_info(loader, response)
        self._get_img_info(loader, response)
        self._get_shop_info(loader, response)

        # extra field
        loader.add_value(
            'created_time',
            datetime.datetime.strftime(
                datetime.datetime.today(), '%Y-%m-%d %H:%M:%S')
        )

        return loader.load_item()

    def _get_product_info(self, loader, response):
        # product info
        loader.add_value('product_url', self.url.strip())
        self.logger.info('==url: %s' % self.url)
        #  product url '^https?://([A-Za-z0-9\-]+\.)+vvic\.com/item/(\d+)$')
        loader.add_value(
            'product_id',
            self.url.strip(), re=r'/(\d+)\.html?')
        loader.add_css(
            'product_name',
            'div.product-intro div.sku-name::text',
            MapCompose(lambda v: v.strip()))

        loader.add_value(
            'product_category_id',
            response.meta.get(
                'category_id',
                re.findall(r'cat\s*:\s*\[([\d,]+)],', response.text)[0]
            )
        )

        loader.add_value(
            'product_img_index_url',
            urljoin(
                response.meta['original_url'],
                str(loader.get_css('img#spec-img::attr(data-origin)')[0])
            )
        )

        # get product details
        for s in response.css('div.p-parameter > ul.parameter2 > li'):
            loader.add_value(
                'product_detail', s.css('::text').extract(),
                lambda v: v[-1].strip().replace('\xa0', ' '))

        # Get price and stock state
        product_id = loader.get_collected_values('product_id')[0]
        vender_id = re.findall(r'venderId\s*:\s*(\d+),', response.text)[0]
        cat = re.findall(r'cat\s*:\s*\[([\d,]+)],', response.text)[0]
        price_url = (
            'https://c0.3.cn/stock?skuId={0}&area=1_72_4137_0&venderId={1}&'
            'cat={2}&buyNum=1&choseSuitSkuIds=&extraParam='
            '{{%22originid%22:%221%22}}&ch=1&fqsp=0&pdpin=&detailedAdd=null'
            '&callback=jQuery172871')
        price_url = price_url.format(product_id, vender_id, cat)
        #  self.logger.info('**price_url: %s' % price_url)
        result = requests.get(price_url)
        result.encoding = 'GBK'
        if result.status_code == 200:
            json_str = re.findall(r'jQuery172871\((.+)\)', result.text)[0]
            stock_dict = json.loads(json_str)
            loader.add_value('product_sale_price',
                             stock_dict['stock']['jdPrice']['p'])
            loader.add_value('product_price_unit', 'CNY')
            loader.add_value(
                'product_status',
                'onshelf' if stock_dict['stock']['skuState'] == 1
                else 'offshelf'
            )
        else:
            self.logger.error('Cannot get price of product %s' % product_id)

    def parse_price_from_http_api(self, response):
        loader = response.meta['loader']

        json_str = re.findall(r'jQuery172871\((.+)\)', response.text)[0]
        price_dict = json.loads(json_str)
        loader.add_value('product_sale_price',
                         price_dict['stock']['jdPrice']['p'])
        #  self.logger.info('***: %s' % price_dict['stock']['jdPrice']['p'])

    def _get_shop_info(self, loader, response):
        # shop info
        loader.add_value('market_id',
                         response.text, re=r"shopId\s*:\s*'(\d+)',")
        loader.add_value('seller_id',
                         response.text, re=r"venderId\s*:\s*(\d+),")
        loader.add_value('market_type', 'shop')
        loader.add_value(
            'market_url',
            urljoin(response.meta['original_url'], str(loader.get_css(
                'div.contact div.J-hove-wrap div.item div.name a::attr(href)',
                TakeFirst()))
            )
        )

        if not re.search(r'^https?://mall.jd.com',
                         loader.get_collected_values('market_url')[0]):
            loader.add_value('market_code',
                             loader.get_collected_values('market_url'),
                             re=r'https?://(\w+)\.jd\.com')
        loader.add_css(
            'market_name',
            'div.contact div.J-hove-wrap div.item div.name a::attr(title)')
        loader.add_value('market_status', '1')

    def _get_attribute_sku_info(self, loader, response):
        # Get sku dictionary
        sku_str_list = re.findall(r'colorSize\s*:\s*(\[.+?]),',
                                  response.text, re.S)
        if sku_str_list:
            sku_str = sku_str_list[0]
        else:
            sku_str = '[]'
        sku_list = json.loads(sku_str)

        sku_id = loader.get_collected_values('product_id')[0]
        #  self.logger.info('**sku_id: %s' % sku_id)
        loader.add_value('sku_id', sku_id)
        for sku in sku_list:
            # sku info
            if str(sku['skuId']) == sku_id:
                sku.pop('skuId')
                loader.add_value('sku_value',
                                 '%s' % json.dumps(sku, ensure_ascii=False))

                #  attribute info
                for attr in sku:
                    loader.add_value('attr_name', attr)
                    loader.add_value('attr_value', [[sku[attr]]])
                    #  self.logger.info(
                    #      '**css: %s' %
                    #      'a[clstag="shangpin|keycount|product|yanse-%s"] > '
                    #      'img::attr(src)' % sku[attr])
                    #  loader.add_css(
                    #      'attr_value_img_url',
                    #      'a[clstag="shangpin|keycount|product|yanse-%s"] > '
                    #      'img::attr(src)' % sku[attr],
                    #      lambda v: ([[
                    #          urljoin(response.meta['original_url'], v[0])]]
                    #          if v else [['']])
                    #  )

                break

        # Have no sku
        if not sku_list:
            loader.add_value('sku_value', '')

        loader.add_value(
            'sku_price',
            loader.get_collected_values('product_sale_price')
        )
        loader.add_value(
            'sku_key',
            re.findall(r"skuidkey\s*:\s*'(\w+)',", response.text)
        )

    def _get_img_info(self, loader, response):
        # image info
        #  self.logger.info('**img: %s' %
        #                   loader.get_css('img#spec-img::attr(data-origin)',
        #                                  re=r'(//.+)jfs/'))
        mid_img_url_base = urljoin(response.meta['original_url'],
                                   loader.get_css(
                                       'img#spec-img::attr(data-origin)',
                                       re=r'(//.+)jfs/')[0])
        small_img_url_base = urljoin(response.meta['original_url'],
                                     loader.get_css(
                                         'li.img-hover > img::attr(src)',
                                         re=r'(//.+)jfs/')[0])
        big_img_url_base = urljoin(response.meta['original_url'],
                                   loader.get_value(
                                       mid_img_url_base,
                                       lambda v: v[0] + '//n0/',
                                       re=r'(//[\w.-]+?)/'))
        img_url_list_match = re.findall(
            r'imageList\s*:\s*(\[.+?]),',
            response.text,
            re.S)
        if img_url_list_match:
            img_url_list = json.loads(img_url_list_match[0])
        else:
            img_url_list = []

        for img_url in img_url_list:
            small_url = small_img_url_base + img_url
            mid_url = mid_img_url_base + img_url
            big_url = big_img_url_base + img_url

            loader.add_value('img_url', small_url)
            loader.add_value('img_url', mid_url)
            loader.add_value('img_url', big_url)

            # for images pipeline
            # loader.add_value('image_urls', big_url)

            # //img14.360buyimg.com/n5/s54x54_jfs/t18286/85/1937544663/60335/fe70148f/5addc747N13eb0a41.jpg
            # //img14.360buyimg.com/n1/s450x450_jfs/t18403/63/1935249568/49837/59c8d6c5/5addc772N4761924e.jpg
            if re.search(r's(\d+[xX]\d+)_', small_url):
                loader.add_value('img_size', small_url, re=r's(\d+[xX]\d+)_')
            else:
                loader.add_value('img_size', '')
            if re.search(r's(\d+[xX]\d+)_', mid_url):
                loader.add_value('img_size', mid_url, re=r's(\d+[xX]\d+)_')
            else:
                loader.add_value('img_size', '')
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

    def parse_from_category_page(self, response):
        """
        Parse category page to get category info, etc.

        Category page:
            https://www.jd.com/allSort.aspx

        Get category tree:
            https://dc.3.cn/category/get?callback=getCategoryCallback
        """

        data_type = response.meta['data_type']
        if data_type == 'category':
            category_url = (
                'https://dc.3.cn/category/get?callback=getCategoryCallback')
            request = scrapy.Request(
                url=category_url,
                callback=self.parse_category_from_category_ajax_page)
            request.meta['original_url'] = category_url
            request.meta['data_type'] = data_type
            request.meta['platform_code'] = response.meta['platform_code']
            yield request

    def parse_category_from_category_ajax_page(self, response):
        """
        Parse category ajax page to get category info.

        Get category tree:
            https://dc.3.cn/category/get?callback=getCategoryCallback
        """

        platform_code = response.meta['platform_code']
        self.original_url = response.meta['original_url']
        self.loader = ItemLoader(item=CategoryPage(), response=response)

        self.loader.add_value('platform_code', platform_code)

        #  json_str = re.findall(r'getCategoryCallback\((.+)\)',
        #                        response.body.decode('gbk', 'unicode-escape'))
        json_str = re.findall(r'getCategoryCallback\((.+)\)',
                              response.body.decode('gbk'))
        if json_str:
            json_str = json_str[0]
        else:
            return None

        category_dict = json.loads(json_str)
        #  category_dict = json.dumps(category_dict, ensure_ascii=False)
        #  category_dict = json.loads(category_dict)
        #  self.logger.info('category:\n%s' % category_dict)
        category_data_list = category_dict.get('data', None)
        if not category_data_list:
            return None
        for cate in category_data_list:
            table_list = cate['t']
            serial = cate['s']
            self._get_category_info_t(table_list, response)
            self._get_category_info_s(serial, response)

        # extra field
        self.loader.add_value(
            'created_time',
            datetime.datetime.strftime(datetime.datetime.today(),
                                       '%Y-%m-%d %H:%M:%S'))
        yield self.loader.load_item()

    def _get_category_info_t(self, table_list, response):
        for s in table_list:
            self._get_category_info_from_category_str(s)

    def _get_category_info_s(self, serial, response):
        """
        """
        for item in serial:
            n = item['n']
            self._get_category_info_from_category_str(n)

            s = item['s']
            for sub_item in s:
                sub_n = sub_item['n']
                self._get_category_info_from_category_str(sub_n)

                sub_s = sub_item['s']
                for sub_sub_item in sub_s:
                    sub_sub_n = sub_sub_item['n']
                    #  print(sub_sub_n)
                    self._get_category_info_from_category_str(sub_sub_n)

    def _get_category_info_from_category_str(self, cate_str):
        """
        The Category string is sperated by '|':
            "jr.jd.com/|金融首页||0"
        """
        cate_list = cate_str.split('|')
        cate_url = cate_list[0]

        if cate_url:
            match = re.match(r'^/?/?([.\w+]+)\.jd\.(com|hk)/?',
                             cate_url.strip())
            # "6144-6167|翡翠玉石||0"
            match1 = re.match(r'^(\d+-\d+-?\d*)', cate_url.strip())
            if match:
                self.loader.add_value(
                    'category_url',
                    urljoin(
                        self.original_url,
                        ('//' + cate_list[0] if
                            re.match(r'[-\w]+\.[-\w]+', cate_list[0])
                            else cate_list[0])
                    )
                )
            elif match1:
                self.loader.add_value(
                    'category_url',
                    'http://list.jd.com/list.html?cat=' + cate_url
                )
            else:
                self.logger.error('Unexpected URL: %s' % cate_url)

            self._get_category_id_from_url(cate_url)

            self.loader.add_value('category_status', '1')
            self.loader.add_value('category_level', '1')
            self.loader.add_value('category_is_leaf', '0')

            self.loader.add_value('category_name', cate_list[1])
        else:
            self.logger.info('Category url is empty. The category string: %s'
                             % cate_str)

    def _get_category_id_from_url(self, cate_url):
            match = re.match(r'^/?/?([.\w+]+)\.jd\.(com|hk)/?',
                             cate_url.strip())

            match1 = re.match(r'^(\d+-\d+-?\d*)', cate_url.strip())
            if match:
                keyword = match.groups()[0]
                org = match.groups()[1]
                if keyword == 'sale':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        re=r'sale\.jd\.com/act/([-\w]+)\.html?')
                    assert re.search(r'sale\.jd\.com/act/([-\w]+)\.html?',
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'coll':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        re=r'coll\.jd\.com/list\.html?\?sub=(\d+)')
                    assert re.search(r'coll\.jd\.com/list\.html?\?sub=(\d+)',
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'channel':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        re=r'channel\.jd\.com/([-\w]+)\.html?')
                    assert re.search(r'channel\.jd\.com/([-\w]+)\.html?',
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'e':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        lambda v: v[0] if v[0] else v[1],
                        re=(r'e\.jd\.com/([-\w]+)\.html?'
                            r'|e\.jd\.com/products/([-\d]+)\.html?'))
                    assert re.search((r'e\.jd\.com/([-\w]+)\.html?'
                                      r'|e\.jd\.com/products/([-\d]+)\.html?'),
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'beauty':
                    self.loader.add_value(
                        'category_id',
                        keyword + '-' + org)
                elif keyword == 'car':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        lambda v: 'car' + '-' + v[0] if v else 'car',
                        re=r'car\.jd\.com/([-\w]*)/?')
                    assert re.search(r'car\.jd\.com/([-\w]*)/?',
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'you':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        lambda v: 'you' + '-' + v[0] + '-' + v[1],
                        #  lambda v: 'you' + '-' + v[0],
                        re=r'you\.jd\.com/([-\w]+)/([-\w]+)\.html?')
                    assert re.search(r'you\.jd\.com/([-\w]+)/([-\w]+)\.html?',
                                     cate_url),\
                        'Cannot get cate ID: %s' % cate_url
                elif keyword == 'list':
                    match2 = re.search(r'ev=([%\w]+)', cate_url)
                    if match2:
                        self.loader.add_value(
                            'category_id',
                            cate_url,
                            lambda v: v[0] + '-' + unquote(v[1]),
                            re=(r'list\.jd\.com/list\.html?\?'
                                r'cat=([,\d]+).*ev=([%\w]+)')
                        )
                        assert re.search((r'list\.jd\.com/list\.html?\?'
                                          r'cat=([,\d]+).*ev=([%\d]+)'),
                                         cate_url),\
                            'Cannot get cate ID: %s' % cate_url
                    else:
                        self.loader.add_value(
                            'category_id',
                            cate_url,
                            lambda v: v[0] if v[0] else v[1],
                            re=(r'list\.jd\.com/list\.html?\?cat=([,\d]+)'
                                r'|list\.jd\.com/list\.html?\?tid=([,\d]+)')
                        )
                        assert re.search(
                            (r'list\.jd\.com/list\.html?\?cat=([,\d]+)'
                             r'|list\.jd\.com/list\.html?\?tid=([,\d]+)'),
                            cate_url),\
                            'Cannot get cate ID: %s' % cate_url
                elif keyword == 'search':
                    self.loader.add_value(
                        'category_id',
                        cate_url,
                        lambda v: unquote(v[0]),
                        re=r'search\.jd\.com/Search\?.*keyword=([%\w]+)')
                    assert re.search(
                        r'search\.jd\.com/Search\?.*keyword=([%\w]+)',
                        cate_url), 'Cannot get cate ID: %s' % cate_url
                else:
                    self.loader.add_value('category_id', keyword)
            elif match1:
                keyword = match1.groups()[0]
                self.loader.add_value(
                    'category_id',
                    keyword)
            else:
                self.logger.error('Unexpected URL for category ID: %s'
                                  % cate_url)

    def parse_from_search_page(self, response):
        """
        Parse product from search page.
        """
        data_type = response.meta['data_type']
        self.item_num = int(response.meta['item_num'])
        self.logger.info('item_num = %s' % self.item_num)
        self.item_count = 0

        if data_type == 'product':
            keyword = response.meta['keyword']
            page_num = response.meta.get('page_num', 1)
            url = ('https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1'
                   '&rt=1&stop=1&vt=2&psort=0&stock=1&page=%s'
                   % (quote(keyword), page_num))

            request = scrapy.Request(
                url=url,
                dont_filter=True,
                callback=self.parse_searched_product_from_search_result_page)
            request.meta['item_num'] = response.meta['item_num']
            request.meta['page_num'] = page_num
            request.meta['keyword'] = response.meta['keyword']
            request.meta['original_url'] = url
            request.meta['platform_code'] = self.platform_code
            yield request

    def parse_searched_product_from_search_result_page(self, response):
        """Parse the search page to get the product info.

        :param str keyword: The searched keyword
        :param str item_num: Number of item whick will be scraped
        """
        self.page_num = response.meta['page_num']
        self.keyword = response.meta['keyword']
        self.platform_code = response.meta['platform_code']
        self.original_url = response.meta['original_url']
        self.sku_list = []
        self.product_request_list = []

        if self.item_num <= self.item_count:
            self.logger.info('0 - last item_count = %s' % self.item_count)
            #  raise scrapy.exceptions.CloseSpider()
            return

        flag = True
        for record in response.css('li[data-sku].gl-item'):
            if (self.item_num <= self.item_count and
                    not self.product_request_list):
                self.logger.info('1 - last item_count = %s' % self.item_count)
                #  raise scrapy.exceptions.CloseSpider()
                return

            if self.item_num <= self.item_count:
                self.logger.info('2 - last item_count = %s' % self.item_count)
                #  raise scrapy.exceptions.CloseSpider()
                #  return
                flag = False

            item_url = record.css(
                'div.gl-i-wrap > div.p-img a::attr(href)'
            ).extract_first()
            item_sku = record.css('::attr(data-sku)').extract_first()
            self.sku_list.append(item_sku)
            if not item_url:
                self.logger.error('The item has no URL: %s' % record.extract())
                continue

            if flag:
                self.product_request_list.append(item_url)

        for item_url in self.product_request_list:
            item_url = urljoin(self.original_url, item_url)
            request = scrapy.Request(
                url=item_url,
                callback=self.parse_product_from_product_page)
            request.meta['original_url'] = item_url
            request.meta['platform_code'] = self.platform_code
            self.item_count += 1
            yield request

        # Get next 30 products in the same webpage
        self.logger.info('item_count: %s' % self.item_count)
        url = ('https://search.jd.com/s_new.php?keyword=%s&enc=utf-8&qrst=1'
               '&rt=1&stop=1&vt=2&stock=1&page=%s&s=30&scrolling=y&tpl=1_M'
               '&show_items=%s') % (quote(self.keyword), self.page_num + 1,
                                    ','.join(self.sku_list))
        headers = {'referer': response.url}
        request = scrapy.Request(
            url=url,
            headers=headers,
            dont_filter=True,
            callback=self._extract_product_from_searched_result_part_page1)
        yield request

    def _extract_product_from_searched_result_part_page1(self, response):
        #  self.logger.info('**keyword: %s' % self.keyword)
        #  self.logger.info('html:\n%s' % response.text)
        for record in response.css('li[data-sku].gl-item'):
            #  self.logger.info('record: %s' % record)
            if self.item_num <= self.item_count:
                self.logger.info('item_num: %s, item_count: %s' %
                                 (self.item_num, self.item_count))
                self.logger.info('last item_count = %s' % self.item_count)
                #  raise scrapy.exceptions.CloseSpider()
                return

            item_url = record.css(
                'div.gl-i-wrap > div.p-img a::attr(href)'
            ).extract_first()
            #  self.logger.info('item_url: %s' % item_url)
            if not item_url:
                self.logger.error('The item has no URL: %s' % record.extract())
                continue

            item_url = urljoin(self.original_url, item_url)
            request = scrapy.Request(
                url=item_url,
                callback=self.parse_product_from_product_page)
            request.meta['original_url'] = item_url
            request.meta['platform_code'] = self.platform_code
            self.item_count += 1
            yield request

        self.logger.info('item_count = %s' % self.item_count)

        url = ('https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1'
               '&rt=1&stop=1&vt=2&psort=0&stock=1&page=%s' % (
                   quote(self.keyword), self.page_num + 2))

        request = scrapy.Request(
            url=url,
            callback=self.parse_searched_product_from_search_result_page)
        request.meta['item_num'] = self.item_num
        request.meta['page_num'] = self.page_num + 2
        request.meta['keyword'] = self.keyword
        request.meta['original_url'] = url
        request.meta['platform_code'] = self.platform_code
        yield request
