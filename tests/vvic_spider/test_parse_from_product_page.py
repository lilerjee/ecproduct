# -*- coding: utf-8 -*-

import unittest
import scrapy
import requests
import sys

from ecproduct.spiders.vvic import VvicSpider


class TestParseFromProductPage(unittest.TestCase):
    """Test method parse_from_product_page"""

    @classmethod
    def setUpClass(cls):
        #  url = 'https://www.vvic.com'
        url = 'https://www.vvic.com/item/8491925'
        entrance_page = 'product'
        data_type = 'product'
        headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
                  }

        cls.spider = VvicSpider(url, entrance_page, data_type)
        cls.request = [r for r in cls.spider.start_requests()][0]
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print('Cannot get page from %s' % url)
            sys.exit(1)
        cls.response = scrapy.http.HtmlResponse(url=url, request=cls.request,
                                            body=r.content, encoding=r.encoding)
        cls.item = cls.spider.parse_from_product_page(cls.response)

    @classmethod
    def tearDownClass(cls):
        del cls.spider
        del cls.request
        del cls.response
        del cls.item

    def test_attr_name_exists(self):
        self.assertTrue('attr_name' in self.item)
        self.assertTrue(self.item['attr_name'])
        self.assertEqual(self.item['attr_name'], ['COLOR', 'SIZE'])

    def test_attr_value_exists(self):
        self.assertTrue('attr_value' in self.item)
        self.assertTrue(self.item['attr_value'])

    def test_attr_value_id_exists(self):
        self.assertTrue('attr_value_id' in self.item)
        self.assertTrue(self.item['attr_value_id'])

    def test_attr_name_value_and_value_id_lenth_is_equal(self):
        self.assertTrue(len(self.item['attr_name']) == 
                        len(self.item['attr_value']) == 
                        len(self.item['attr_value_id']))

    def test_img_url_exists(self):
        self.assertTrue('img_url' in self.item)
        self.assertTrue(self.item['img_url'])

    def test_img_description_exists(self):
        self.assertTrue('img_description' in self.item)
        self.assertTrue(self.item['img_description'])

    def test_img_purpose_exists(self):
        self.assertTrue('img_purpose' in self.item)
        self.assertTrue(self.item['img_purpose'])

    def test_img_size_exists(self):
        self.assertTrue('img_size' in self.item)
        self.assertTrue(self.item['img_size'])

    def test_img_size_url_purpose_description_length_is_equal(self):
        self.assertTrue(len(self.item['img_url']) == 
                        len(self.item['img_size']) == 
                        len(self.item['img_description']) == 
                        len(self.item['img_purpose']))

    def test_market_addr_exists(self):
        self.assertTrue('market_addr' in self.item)
        self.assertTrue(self.item['market_addr'])

    def test_market_id_exists(self):
        self.assertTrue('market_id' in self.item)
        self.assertTrue(self.item['market_id'])

    def test_market_name_exists(self):
        self.assertTrue('market_name' in self.item)
        self.assertTrue(self.item['market_name'])

    def test_market_type_exists(self):
        self.assertTrue('market_type' in self.item)
        self.assertTrue(self.item['market_type'])

    def test_market_item_num_exists(self):
        self.assertTrue('market_item_num' in self.item)
        self.assertTrue(self.item['market_item_num'])

    def test_market_url_exists(self):
        self.assertTrue('market_url' in self.item)
        self.assertTrue(self.item['market_url'])

    def test_product_detail_exists(self):
        self.assertTrue('product_detail' in self.item)
        self.assertTrue(self.item['product_detail'])

    def test_product_id_exists(self):
        self.assertTrue('product_id' in self.item)
        self.assertTrue(self.item['product_id'])

    def test_product_name_exists(self):
        self.assertTrue('product_name' in self.item)
        self.assertTrue(self.item['product_name'])

    def test_product_price_unit_exists(self):
        self.assertTrue('product_price_unit' in self.item)
        self.assertTrue(self.item['product_price_unit'])

    def test_product_sale_price_exists(self):
        self.assertTrue('product_sale_price' in self.item)
        self.assertTrue(self.item['product_sale_price'])

    def test_product_source_id_exists(self):
        self.assertTrue('product_source_id' in self.item)
        self.assertTrue(self.item['product_source_id'])

    def test_product_source_price_exists(self):
        self.assertTrue('product_source_price' in self.item)
        self.assertTrue(self.item['product_source_price'])

    def test_product_source_price_unit_exists(self):
        self.assertTrue('product_source_price_unit' in self.item)
        self.assertTrue(self.item['product_source_price_unit'])

    def test_product_source_url_exists(self):
        self.assertTrue('product_source_url' in self.item)
        self.assertTrue(self.item['product_source_url'])

    def test_product_status_exists(self):
        self.assertTrue('product_status' in self.item)
        self.assertTrue(self.item['product_status'])

    def test_product_upload_time_exists(self):
        self.assertTrue('product_upload_time' in self.item)
        self.assertTrue(self.item['product_upload_time'])

    def test_product_url_exists(self):
        self.assertTrue('product_url' in self.item)
        self.assertTrue(self.item['product_url'])

    def test_sku_id_exists(self):
        self.assertTrue('sku_id' in self.item)
        self.assertTrue(self.item['sku_id'])

    def test_sku_price_exists(self):
        self.assertTrue('sku_price' in self.item)
        self.assertTrue(self.item['sku_price'])

    def test_sku_value_exists(self):
        self.assertTrue('sku_value' in self.item)
        self.assertTrue(self.item['sku_value'])

    def test_sku_id_value_price_lenth_is_equal(self):
        self.assertTrue(len(self.item['sku_id']) ==
                        len(self.item['sku_price']) ==
                        len(self.item['sku_value']))


if __name__ == '__main__':
    unittest.main()
