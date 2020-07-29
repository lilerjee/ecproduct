# -*- coding: utf-8 -*-
r"""
* Commands to run 1688 Spider:

  #. Add right URLs to `input/1688_url_test.txt` or `input/1688_url.txt`.
  #. Run the following commands.

     * Get product info from product page::

        $ python main.py 1688 product product -f test

     * Get market info from website index page::

        $ python main.py 1688 index market -f test

     * Get category info from reaserch index page::

        $ python main.py 1688 search category -f test

     * Get all products info of the market from market page::

        $ python main.py 1688 market product -f test

     * Get all products info of the website from website index page::

        $ python main.py 1688 index product -f test

     * Get all products info from search page according to one keyword::

        $ python main.py 1688 search product -f test -a keyword=衬衫 -a item_num=100 -a city=gz
"""
from __future__ import print_function
from __future__ import unicode_literals
import scrapy
from ecproduct.items import ProductPage
# from ecproduct.items import MarketPage, IndexPage, SearchPage, ContactPage
from scrapy.loader import ItemLoader
from scrapy.loader.processors import Compose
# from scrapy.loader.processors import TakeFirst, Compose
from ecproduct.spiders.ecproduct import EcproductSpider
# from scrapy.http.response import urljoin
from urllib.parse import unquote, quote
# from log import Log
import os
# import sys
import json
import re
import datetime


class A1688Spider(scrapy.Spider):
    name = '1688'
    allowed_domains = ['1688.com']
    platform_code = 'A1688'
    # start_urls = ['http://1688.com/']

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
        'DOWNLOAD_DELAY': 10,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DOWNLOAD_TIMEOUT': 5,
    }

    def __init__(self, url, entrance_page, data_type,
                 home_item_id=None, platform_code=platform_code, keyword='',
                 item_num='100'):

        EcproductSpider.__init__(
            self, url=url, entrance_page=entrance_page,
            data_type=data_type, home_item_id=home_item_id,
            platform_code=platform_code, keyword=keyword,
            item_num=item_num)

    def start_requests(self):
        return EcproductSpider.start_requests(self)

    def parse_product_from_product_page(self, response):
        """
        Parse product detail page.

        * Product URL example:

            - Unshelf product:

              https://detail.1688.com/offer/543884257260.html

            - product which has three price range:

              https://detail.1688.com/offer/544560773525.html

            - product which has three price and discount price range:

              https://detail.1688.com/offer/539065306832.html

            - product which has only one price range:

              https://detail.1688.com/offer/40976180711.html
              https://detail.1688.com/offer/543218337857.html

        """
        self.url = response.meta['original_url']
        loader = ItemLoader(item=ProductPage(), response=response)

        # plaftform info
        loader.add_value('platform_code', response.meta['platform_code'])
        loader.add_value(
            'product_category_id',
            response.meta.get('category_id', ''))

        # determin whether the product is deleted,
        # or if the webpage is found, or the product is unshelf.
        error_url = 'http://page.1688.com/shtml/static/wrongpage.html'
        error_match = re.match(error_url, response.request.url)
        if error_match:
            error_text = response.css(
                'div.header > h3.title > em.highlight::text'
            ).extract_first()
            if error_text == '查找的商品已删除':
                loader.add_value(
                    'product_id', self.url.strip(),
                    Compose(lambda v: v[-1]), re=r'(\d+)\.html')
                loader.add_value('product_url', self.url.strip())
                loader.add_value('product_status', 'deleted')
            elif error_text == 'Error 404':
                loader.add_value(
                    'product_id', self.url.strip(),
                    Compose(lambda v: v[-1]), re=r'(\d+)\.html')
                loader.add_value('product_url', self.url.strip())
                loader.add_value('product_status', 'nonexistent')
            else:
                self.logger.error('other error happened: %s' % error_text)

        elif response.css('div.mod-detail-offline') and (
                '商品已下架' in
                response.css('h3.mod-detail-offline-title').extract_first()):

                loader.add_value(
                    'product_id', self.url.strip(), re=r'(\d+)\.html')
                loader.add_value('product_url', self.url.strip())
                loader.add_value('product_status', 'unshelf')
        else:
            self._get_product_info(loader, response)
            self._get_attribute_sku_info(loader, response)
            self._get_img_info(loader, response)
            self._get_shop_info(loader, response)

        # extra field
        loader.add_value('created_time', datetime.datetime.strftime(
            datetime.datetime.today(), '%Y-%m-%d %H:%M:%S'))

        return loader.load_item()

    def _get_product_info(self, loader, response):
        # product info
        loader.add_value('product_url', self.url.strip())
        # product url '^https?://([A-Za-z0-9\-]+\.)+vvic\.com/item/(\d+)$')
        loader.add_value('product_id', self.url.strip(), re=r'(\d+)\.html?')
        loader.add_value('product_status', 'onshelf')
        loader.add_css(
            'product_name', 'div#mod-detail-title > h1.d-title::text')

        # get price range
        price_table = response.css('div#mod-detail-price div.d-content table')

        price_data_list = [
            e.extract() for e in
            price_table.css('tr.price td span.value::text') if e]
        original_price_data_list = [
            e.extract() for e in
            price_table.css('tr.original-price td span.value::text') if e]
        amount_data_list = [
            e.extract() for e in
            price_table.css('tr.amount td span.value::text') if e]

        if price_data_list:
            loader.add_value('product_sale_price', price_data_list[0])
        if original_price_data_list:
            loader.add_value(
                'product_original_range_price',
                '{' + ', '.join(
                    '"%s":"%s"' % (a, b) for (a, b) in
                    zip(amount_data_list, original_price_data_list)) + '}')
        if price_data_list:
            loader.add_value(
                'product_range_price',
                '{' + ', '.join(
                    '"%s":"%s"' % (a, b) for (a, b) in
                    zip(amount_data_list, price_data_list)) + '}')

        loader.add_value('product_price_unit', 'CNY')

        loader.add_css(
            'product_img_index_url',
            'div#dt-tab li.tab-trigger.active::attr(data-imgs)',
            re=r'{"preview"\s*:\s*"(.*?)"')

        # get product detail
        content_table = response.css(
            'div#mod-detail-attributes div.obj-content table')
        for tr in content_table.css('tr'):
            key = tr.css('td.de-feature::text').extract()
            value = tr.css('td.de-value::text').extract()
            loader.add_value(
                'product_detail', [
                    '%s: %s' % (a, b) for (a, b)
                    in zip(key, value)])

    def _get_attribute_sku_info(self, loader, response):
        # attribute info
        attr_dict = json.loads(
            re.findall(
                r'var\s+iDetailData\s+=\s+({.*?});',
                response.text, re.S)[0])
        for attr in attr_dict.get('sku', {}).get('skuProps', []):
            loader.add_value('attr_name', attr.get('prop', ''))
            name_list = []
            img_list = []
            for v in attr.get('value', []):
                name_list.append(v.get('name', ''))
                img_list.append(v.get('imageUrl', ''))
            loader.add_value('attr_value', [name_list])
            loader.add_value('attr_value_img_url', [img_list])

        # sku info
        sku_all = attr_dict.get('sku', {}).get('skuMap', [])
        for sku_key in sku_all:
            loader.add_value('sku_id', str(sku_all[sku_key]['skuId']))
            loader.add_value('sku_value', sku_key.replace('&gt;', ' | '))
            loader.add_value(
                'sku_price', sku_all[sku_key].get('discountPrice')
                if sku_all[sku_key].get('discountPrice', None) else
                loader.get_collected_values('product_sale_price'))
            loader.add_value(
                'sku_sale_count',
                sku_all[sku_key].get('saleCount'))
            loader.add_value(
                'sku_can_book_count',
                sku_all[sku_key].get('canBookCount'))

    def _get_img_info(self, loader, response):
        # image info
        for s in response.css('div#dt-tab ul > li.tab-trigger'):
            small_url = (
                s.css('div a img::attr(data-lazy-src)').extract_first()
                if (s.css('div a img::attr(data-lazy-src)'))
                else s.css('div a img::attr(src)').extract_first())
            data_imgs = s.css('::attr(data-imgs)').extract_first()
            data_imgs = json.loads(data_imgs)
            mid_url = data_imgs.get('preview')
            big_url = data_imgs.get('original')
            loader.add_value('img_url', small_url)
            loader.add_value('img_url', mid_url)
            loader.add_value('img_url', big_url)
            # loader.add_value('image_urls', big_url)    # for images pipeline
            loader.add_value('img_size', small_url, re=r'\.(\d+[xX]\d+)\.')
            loader.add_value('img_size', mid_url, re=r'\.(\d+[xX]\d+)\.')
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

    def _get_shop_info(self, loader, response):
        # shop info
        loader.add_css(
            'market_url',
            'div.app-smt_supplierInfoSmall div.nameArea a.name::attr(href)',
            re=r'(http.*\.html?)\??')
        loader.add_css(
            'market_name',
            'div.app-smt_supplierInfoSmall div.nameArea a.name::attr(title)')
        loader.add_value(
            'market_code',
            loader.get_collected_values('market_url'),
            re=r'https?://(\w+)\.1688\.com')
        loader.add_value(
            'market_id',
            response.text,
            re=r"'memberid'\s*:\s*'([-\w]+)',")
        loader.add_value('market_type', 'shop')
        loader.add_css(
            'market_contact_wangwang',
            'div.detail div.contactSeller span.wangwang::attr(data-nick)',
            lambda v: unquote(v[0]))
        loader.add_css(
            'market_addr',
            'div.detail div.address span.disc::text')
        loader.add_css(
            'market_exist_time',
            'div.content span.year-number::text')
        loader.add_value('market_status', '1')

    def parse_from_index_page(self, response):
        """
        Index URL: https://www.1688.com/

        #. Parse category:

           Category type:

           - There is category ID.

             URL: https://fuzhuang.1688.com/nvzhuang
        """

    def parse_from_search_page(self, response):
        """
        """
        data_type = response.meta['data_type']

        if data_type == 'product':
            keyword = response.meta['keyword']
            url = ('https://s.1688.com/selloffer/offer_search.htm?keywords=%s'
                   % quote(keyword))

            request = scrapy.Request(
                url=url,
                callback=self.parse_searched_product_from_search_result_page)
            request.meta['item_num'] = response.meta['item_num']
            page_num = (response.meta.get('page_num') if
                        response.meta.get('page_num', None) else '1')
            request.meta['page_num'] = page_num
            request.meta['keyword'] = response.meta['keyword']
            request.meta['original_url'] = url
            request.meta['platform_code'] = self.platform_code
            yield request

    def parse_searched_product_from_search_result_page(self, response):
        """Parse the search page to get the product info.
        The result page not only include product, but also include shop.

        :param str keyword: The searched keyword
        :param str item_num: Number of item whick will be scraped
        """
        page_num = response.meta['page_num']
        item_num = int(response.meta['item_num'])
        self.logger.info('item_num = %s' % item_num)
        item_count = 0

        for record in response.css('ul#sm-offer-list > li.sm-offer-item'):
            item_url = record.css(
                'div.sm-offer-photo > a.sm-offer-photoLink::attr(href)'
            ).extract_first()
            if not item_url:
                continue
            request = scrapy.Request(
                url=item_url,
                callback=self.parse_product_from_product_page)
            request.meta['original_url'] = item_url
            request.meta['platform_code'] = self.platform_code
            item_count += 1
            yield request

            if item_num <= item_count:
                self.logger.info('last item_count = %s' % item_count)
                return

        self.logger.info('item_count = %s' % item_count)
        keyword = response.meta['keyword']
        url = ('https://s.1688.com/selloffer/offer_search.htm'
               '?keywords=%s#beginPage=%s'
               % (quote(keyword), str(int(page_num) + 1)))

        request = scrapy.Request(
            url=url,
            callback=self.parse_searched_product_from_search_result_page)
        request.meta['item_num'] = item_num - item_count
        request.meta['page_num'] = str(int(page_num) + 1)
        request.meta['data_type'] = 'product'
        request.meta['platform_code'] = self.platform_code
        request.meta['keyword'] = response.meta['keyword']
        yield request
