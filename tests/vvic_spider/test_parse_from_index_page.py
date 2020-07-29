# -*- coding: utf-8 -*-

import unittest
import scrapy
import requests
import sys

from ecproduct.spiders.vvic import VvicSpider


class TestParseFromIndexPage(unittest.TestCase):
    """Test method parse_from_index_page"""

    @classmethod
    def setUpClass(cls):
        url = 'https://www.vvic.com'
        entrance_page = 'index'
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
        cls.item_generator = cls.spider.parse_from_index_page(cls.response)
        for i in cls.item_generator:
            if isinstance(i, scrapy.http.Request):
                continue
            else:
                cls.item = i
                break
        #  print(cls.item)

    @classmethod
    def tearDownClass(cls):
        del cls.spider
        del cls.request
        del cls.response
        del cls.item_generator
        del cls.item

    def test_market_addr_exists(self):
        self.assertTrue('market_addr' in self.item)
        self.assertTrue(self.item['market_addr'])

    def test_market_code_exists(self):
        self.assertTrue('market_code' in self.item)
        self.assertTrue(self.item['market_code'])

    def test_market_id_exists(self):
        self.assertTrue('market_id' in self.item)
        self.assertTrue(self.item['market_id'])

    def test_market_name_exists(self):
        self.assertTrue('market_name' in self.item)
        self.assertTrue(self.item['market_name'])

    def test_market_name_equal_assumption(self):
        self.assertEqual(
            set(self.item['market_name']),
            set(['广州', '普宁', '解放南鞋城', '新塘', '杭州男装']))

    def test_market_status_exists(self):
        self.assertTrue('market_status' in self.item)
        self.assertTrue(self.item['market_status'])

    def test_market_type_exists(self):
        self.assertTrue('market_type' in self.item)
        self.assertTrue(self.item['market_type'])

    def test_market_url_exists(self):
        self.assertTrue('market_url' in self.item)
        self.assertTrue(self.item['market_url'])

    def test_market_url_equal_assumption(self):
        self.assertEqual(
            set(self.item['market_url']),
            set(['https://www.vvic.com/gz',
                'https://www.vvic.com/pn',
                'https://www.vvic.com/jfn',
                'https://www.vvic.com/xt',
                'https://www.vvic.com/hz'])
        )

    def test_parent_market_id_exists(self):
        self.assertTrue('parent_market_id' in self.item)
        self.assertTrue(self.item['parent_market_id'])

    def test_market_id_addr_code_name_status_type_url_length_is_equal(self):
        self.assertTrue(len(self.item['market_addr']) == 
                        len(self.item['market_code']) == 
                        len(self.item['market_id']) == 
                        len(self.item['market_name']) == 
                        len(self.item['market_status']) == 
                        len(self.item['market_type']) == 
                        len(self.item['market_url']))

if __name__ == '__main__':
    unittest.main()
