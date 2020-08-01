.. _user:

User Guide of ECProduct
=======================

Structure of the Project
------------------------

- **database**
    The database file for storing scraped data into database.
- **docs**
    Plan files, Design files, API reference, User guide, etc.
- **ecproduct**
    Crawler code.
- **input**
    | Input data for crawler. 
    | <domain>_url.txt for production environment.
    | <domain>_url_text.txt for test environment.
- **log**
    Log files.
- **output**
    Output files.
- **web**
    Web API, Web management APP.
- **main.py**
    Entrance file for crawler.
    Run it for test or production environment.
- **scrapy.cfg**
    Scrapy configuration file for this project.


How to use ECProduct
--------------------

- **Usage**
    :: 

        $  python main.py -h
        usage: main.py [-h] (-f URL-FILE-TYPE | -u [URL [URL ...]])
                       [-p [HOME_PLATFORM_ITEM_ID [HOME_PLATFORM_ITEM_ID ...]]]
                       [-a NAME=VALUE]
                       spider_name entrance_page_name scrape_data_type

        Command line interface for spiders.

        positional arguments:
          spider_name           Platform or spider name(e.g. wsy, vvic, jd, 1688).
          entrance_page_name    Entrance page name to be scraped(e.g. product, market,
                                index, search).
          scrape_data_type      Data type to be scraped(e.g. product, category,
                                market).

        optional arguments:
          -h, --help            show this help message and exit
          -f URL-FILE-TYPE, --url-file-type URL-FILE-TYPE
                                Environment name, or URL file type, which will affect
                                the sourcefile from which the input(e.g. test,
                                product).
          -u [URL [URL ...]], --url [URL [URL ...]]
                                URL to be scraped.If applying this option, ignore
                                environment argument.
          -p [HOME_PLATFORM_ITEM_ID [HOME_PLATFORM_ITEM_ID ...]], --home-platform-item-id [HOME_PLATFORM_ITEM_ID [HOME_PLATFORM_ITEM_ID ...]]
                                Item ID for the product of other platform.It should be
                                paired with --url argument if present.
          -a NAME=VALUE         Set spider argument (may be repeated)

- **Get input data from Test Environment File**
    For example::

        $ python main.py 1688 product product -f test

- **Get input data from Production Environment File**
    For example::

        $ python main.py 1688 product product -f product

- **Get input data from command line**
    For example::

        $ python main.py vvic product product -u https://www.vvic.com/item/5669615 https://www.vvic.com/item/3718281


VVIC Spider
-----------

* Explanation of VVIC Spider

  #. Get **website** info from contact page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_contact_page`

  #. Get **'city' market** info from website index page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_index_page`

  #. Get **'mall' market** list from city index page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_city_index_page`

  #. Get **'floor' market** info and **'shop' market** info from mall index page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_mall_index_page`

  #. Get **category** info from search index page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_search_page`

  #. Get **all product detail** info from shop index page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_market_shop_page`
     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_from_market_with_product_page_pagination`

  #. Get **one product detail** info from product page

     :meth:`~ecproduct.spiders.vvic.VvicSpider.parse_product_from_product_page`

* Commands to run VVIC Spider:

  #. Add right URLs to `input/vvic_url_test.txt` or `input/vvic_url.txt`.
  #. Run the following commands.
     
     * Get product info from product page::

        $ python main.py vvic product product -f test

     * Get market info from website index page::

        $ python main.py vvic index market -f test

     * Get category info from reaserch index page::

        $ python main.py vvic search category -f test

     * Get all products info of the market from market page::

        $ python main.py vvic market product -f test

     * Get all products info of the website from website index page::

        $ python main.py vvic index product -f test

     * Get all products info from search page according to one keyword::

         $ python main.py vvic search product -f test -a keyword=衬衫 -a item_num=100 -a city=gz

1688 Spider
-----------

.. automodule:: ecproduct.spiders.a1688

JD Spider
-----------

.. automodule:: ecproduct.spiders.jd

Unit test for spiders
---------------------

* Usage

  Go to the project directory, then run the following command.

  Run all test cases::

    $ python -m unittest discover tests

  Run one package's test cases::

    $ python -m unittest discover tests\vvic_spider

  Run one moudle's test cases::

    $ python -m unittest tests\vvic_spider\test_parse_from_product_page.py

  Run one test case::

    $ python -m unittest tests.vvic_spider.test_parse_from_product_page.test_attr_value_id_exists

  Run all test cases and output verbose info::

    $ python -m unittest discover -v tests

