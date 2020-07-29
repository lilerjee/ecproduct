# coding=utf-8
"""
Command line interface for spiders.
Start spiders with process.

How to use ECProduct
--------------------

- **Get input data from Test Environment File**
    For example::

        $ py -3 main.py 1688 product product -f test

- **Get input data from Production Environment File**
    For example::

        $ py -3 main.py 1688 product product -f product

- **Get input data from command line**
    For example::

        $ python main.py vvic product product -u https://www.vvic.com/item/5669615 https://www.vvic.com/item/3718281

"""

from __future__ import print_function
from __future__ import unicode_literals
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import sys
import re
import os
import argparse
import logging


#  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

parser = argparse.ArgumentParser(
    description='Command line interface for spiders.'
)

parser.add_argument(
    'spider_name',
    choices=['wsy', 'vvic', 'jd', '1688', 'tmall', 'amazon', 'mogujie',
             'taobao'],
    metavar='spider_name',
    help=('Platform or spider name'
          '(e.g. wsy, vvic, jd, 1688).')
)
parser.add_argument(
    'entrance_page_name',
    metavar='entrance_page_name',
    choices=['product', 'market', 'index', 'search', 'category'],
    help=('Entrance page name to be scraped'
          '(e.g. product, market, index, search).')
)
parser.add_argument(
    'scrape_data_type',
    choices=['product', 'category', 'market'],
    metavar='scrape_data_type',
    help=('Data type to be scraped'
          '(e.g. product, category, market).')
)

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument(
    '-f',
    '--url-file-type',
    choices=['test', 'product'],
    metavar='URL-FILE-TYPE',
    help=('Environment name, or URL file type, '
          'which will affect the source'
          'file from which the input'
          '(e.g. test, product).')
)
group.add_argument(
    '-u',
    '--url',
    nargs='*',
    action='append',
    help=('URL to be scraped.'
          'If applying this option, ignore environment argument.'),
)

parser.add_argument(
    '-p',
    '--home-platform-item-id',
    nargs='*',
    action='append',
    help=('Item ID for the product of other platform. '
          'It should be paired with --url argument if present.')
)
parser.add_argument(
    '-a',
    metavar='NAME=VALUE',
    action='append',
    help=('Set spider argument (may be repeated)')
)
args = parser.parse_args()

#  logger.info(args)
#  sys.exit()

url = []
home_item_id = []
if args.url_file_type:
    input_dir = 'input'
    file_encoding = 'utf-8'

    url_file = (input_dir + os.path.sep + '%s_url.txt' % args.spider_name
                if args.url_file_type == 'product' else
                input_dir + os.path.sep + '%s_url_%s.txt' %
                (args.spider_name, args.url_file_type))
    f = open(url_file, encoding=file_encoding)

    # Ignore blank lines and ones which start '#'
    # Remove duplicated line
    args_sperator = None
    line_set = {tuple(line.strip().split(sep=args_sperator)) for line in f
                if line.strip() and not re.findall(r'^#.*', line.strip())}
    logger.info('Number of lines to be processed: %s' % len(line_set))

    for line in line_set:
        if len(line) == 2:
            url.append(line[1])
            home_item_id.append(line[0])
        elif len(line) == 1:
            url.append(line[0])
        else:
            logger.error('Permit only tow columns in URL input file:'
                         'key and url')
            sys.exit(1)
else:
    url = [u for sublist in args.url for u in sublist]
    if args.home_platform_item_id:
        home_item_id = args.home_platform_item_id

spider_args = dict(v.split('=') for v in args.a) if args.a else {}

process = CrawlerProcess(get_project_settings())
process.crawl('%s' % args.spider_name,
              url=url, home_item_id=home_item_id,
              entrance_page=args.entrance_page_name,
              data_type=args.scrape_data_type, **spider_args)
process.start()
