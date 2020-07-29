# -*- coding: utf-8 -*-

# Scrapy settings for ecproduct project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os

PROJECT_BASE_PATH = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))

BOT_NAME = 'ecproduct'

SPIDER_MODULES = ['ecproduct.spiders']
NEWSPIDER_MODULE = 'ecproduct.spiders'

# FEED_URI='file:///' + PROJECT_BASE_PATH + os.path.sep + 'log' + os.path.sep + 'ecproduct.jl'  
# FEED_EXPORT_ENCODING='utf-8'
# FEED_EXPORT_ENCODING='gb2312'
# FEED_FORMAT='csv'
# FEED_FORMAT='jsonlines'
# FEED_EXPORT_FIELDS=['product_color_id','product_color_name','product_id','product_index_img_url','product_link_id','product_link_price']

# log
LOG_ENABLED = True
LOG_ENCODING = 'utf-8'
LOG_FILE = PROJECT_BASE_PATH + os.path.sep + 'log' + os.path.sep + 'ecproduct.log'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_LEVEL = 'DEBUG'
# LOG_LEVEL = 'INFO'
# LOG_STDOUT = True

RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408]

# DUPEFILTER_CLASS = 'ecproduct.middlewares.CustomFilter'
# DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ecproduct (+http://www.yourdomain.com)'
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0'


# Setting DUPEFILTER_DEBUG to True will make it log all duplicate requests.
DUPEFILTER_DEBUG = True

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

MYSQL_HOST = 'localhost'
MYSQL_USERNAME = 'ecproduct'
MYSQL_PASSWORD = 'ecproduct@pwd'
MYSQL_DATABASE = 'ecproduct'
# MYSQL_DATABASE = 'aims'
MYSQL_CHARSET = 'utf8'

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 5
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 5
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'ecproduct.middlewares.EcproductSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
#    'ecproduct.middlewares.MyCustomDownloaderMiddleware': 543,
        'scrapy.downloadermiddleware.useragent.UserAgentMiddleware': None,
        'ecproduct.middlewares.RotateUserAgentMiddleware': 400
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'ecproduct.pipelines.EcproductPipeline': 300,
   # 'scrapy.pipelines.images.ImagesPipeline': 1,     # For images pipeline
}

IMAGES_STORE = PROJECT_BASE_PATH + '/output/images'
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (270, 270),
}
# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
