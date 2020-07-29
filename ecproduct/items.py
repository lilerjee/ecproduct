# -*- coding: utf-8 -*-
"""
scraped information definition.
one item class is mapped to one part of webpage or one table of database or
one webpage.
the column name of corresponding table is the same with the filed name of item.
platform_code and product_id can ensure only one product

status - specify the record status. 0 : created; 1+ : updated, -1 : deleted.
         the value of 'updated' is the number of  update times
"""

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
#  import datetime


class Attribute(scrapy.Item):
    """
    `primary_key` defines primary key of table.
    `combination` defines combination relationship between fields
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    product_id = scrapy.Field(primary_key=True, foreign_key=True)
    attr_name_id = scrapy.Field(combination='1')
    attr_name = scrapy.Field(combination='1')
    attr_value_id = scrapy.Field(combination='N')
    attr_value = scrapy.Field(combination='N', primary_key=True)
    attr_value_img_url = scrapy.Field(combination='N')
    status = scrapy.Field(status=True)
    # use it only when creating the item
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class Sku(scrapy.Item):
    """
    `primary_key` defines primary key of table.
    `combination` defines combination relationship between fields
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    product_id = scrapy.Field(primary_key=True, foreign_key=True)
    sku_id = scrapy.Field(primary_key=True, combination='1')
    sku_key = scrapy.Field(combination='1')
    #  sku_value = scrapy.Field(primary_key=True, combination='1')
    sku_value = scrapy.Field(combination='1')
    sku_sale_count = scrapy.Field(combination='1')
    sku_can_book_count = scrapy.Field(combination='1')
    sku_price = scrapy.Field(combination='1')
    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class Image(scrapy.Item):
    """
    `primary_key` defines primary key of table.
    `combination` defines combination relationship between fields
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    product_id = scrapy.Field(primary_key=True, foreign_key=True)
    img_url = scrapy.Field(primary_key=True, combination='1')
    img_size = scrapy.Field(combination='1')
    img_purpose = scrapy.Field(combination='1')
    img_description = scrapy.Field(combination='1')
    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)

    # used for image pipeline
    image_urls = scrapy.Field()
    images = scrapy.Field()


class Product(scrapy.Item):
    """
    货源网站商品信息
    `primary_key` defines primary key of table.
    `combination` defines combination relationship between fields
    """

    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    product_id = scrapy.Field(primary_key=True, foreign_key=True)

    market_id = scrapy.Field()
    product_status = scrapy.Field()         # 商品状态：下架，上架，缺货，不能访问等
    product_name = scrapy.Field()
    product_url = scrapy.Field(primary_key=True)
    product_original_range_price = scrapy.Field()
    product_sale_price = scrapy.Field()
    product_range_price = scrapy.Field()
    product_price_unit = scrapy.Field()
    product_category_id = scrapy.Field()
    product_quantity = scrapy.Field()
    product_art_no = scrapy.Field()         # 货号
    product_detail = scrapy.Field()         # 商品详情
    product_img_index_url = scrapy.Field()  # 索引图片链接
    product_upload_time = scrapy.Field()    # 商品上新时间
    product_unshelf_time = scrapy.Field()   # 商品下架时间

    product_source_id = scrapy.Field()      # 链接网站对应商品ID
    product_source_url = scrapy.Field()     # 链接网站对应商品url
    product_source_price = scrapy.Field()   # 链接网站对应商品price
    product_source_price_unit = scrapy.Field()

    # 本站相关信息
    home_item_id = scrapy.Field()
    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)

# class Shop(scrapy.Item):
    # """
    # 货源网站店铺信息
    # """
    # # 货源网站代号
    # platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    # shop_id = scrapy.Field(primary_key=True, foreign_key=True)

    # shop_name = scrapy.Field()
    # shop_url = scrapy.Field(primary_key=True)
    # shop_rank = scrapy.Field()
    # shop_product_num = scrapy.Field()   # 店铺商品数量

    # shop_contact_wangwang = scrapy.Field()
    # shop_contact_phone = scrapy.Field()
    # shop_contact_weixin = scrapy.Field()    # 卖家微信
    # shop_contact_qq = scrapy.Field()
    # shop_contact_addr = scrapy.Field()
    # shop_contact_area = scrapy.Field()       # 产地

    # seller_id = scrapy.Field()

    # status = scrapy.Field(status=True)
    # created_time = scrapy.Field(create=True)
    # deleted_time = scrapy.Field(delete=True)


class Market(scrapy.Item):
    """
    货源网站市场、店铺、站点等商品买卖地址信息
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    # 可以人造id，用id-<number>描述属于该市场的哪个楼层或者分区
    market_id = scrapy.Field(primary_key=True,
                             foreign_key=True,
                             combination='1')
    market_code = scrapy.Field(combination='1')
    market_status = scrapy.Field(combination='1')  # 1 - onshelf, 0 - unshelf
    # 市场具有层级关系，用该字段进行联系与描述
    parent_market_id = scrapy.Field(combination='1')
    # 市场类型：店铺，商场（市场），站点，楼层，区域（A区，B区), website
    market_type = scrapy.Field(combination='1')

    # info of related product, e.g.: accessing one shop url will jump
    # to other platform url(taobao url will jump to tmall)
    related_type = scrapy.Field()   # e.g. jump
    related_platform_code = scrapy.Field()
    related_market_id = scrapy.Field()
    related_market_url = scrapy.Field()

    market_name = scrapy.Field(combination='1')
    market_url = scrapy.Field(primary_key=True,
                              foreign_key=True, combination='1')
    market_rank = scrapy.Field()

    market_item_num = scrapy.Field(combination='1')   # 市场内项目数量

    market_contact_wangwang = scrapy.Field(combination='1')
    market_contact_phone = scrapy.Field(combination='1')
    market_contact_weixin = scrapy.Field(combination='1')    # 卖家微信
    market_contact_qq = scrapy.Field(combination='1')
    market_contact_mail = scrapy.Field(combination='1')

    market_addr = scrapy.Field(combination='1')

    market_start_time = scrapy.Field(combination='1')
    market_exist_time = scrapy.Field(combination='1')

    seller_id = scrapy.Field()

    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class Market_Attr(scrapy.Item):
    """
    货源网站市场属性信息
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    # 可以人造id，用id-<number>描述属于该市场的哪个楼层或者分区
    market_id = scrapy.Field(primary_key=True, foreign_key=True)

    market_attr_type = scrapy.Field(primary_key=True, combination='1')
    market_attr_name_id = scrapy.Field(combination='1')
    market_attr_name = scrapy.Field(primary_key=True, combination='1')
    market_attr_value_id = scrapy.Field(combination='1')
    market_attr_value = scrapy.Field(primary_key=True, combination='1')

    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class Seller(scrapy.Item):
    """
    货源网站卖家信息
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    seller_id = scrapy.Field(primary_key=True)
    market_id = scrapy.Field()
    seller_name = scrapy.Field()

    seller_contact_wangwang = scrapy.Field()
    seller_contact_phone = scrapy.Field()
    seller_contact_weixin = scrapy.Field()    # 卖家微信
    seller_contact_qq = scrapy.Field()
    seller_contact_addr = scrapy.Field()
    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class Category(scrapy.Item):
    """
    货源网站商品品类信息
    """
    # 货源网站代号
    platform_code = scrapy.Field(primary_key=True, foreign_key=True)
    category_id = scrapy.Field(primary_key=True, foreign_key=True,
                               combination='1')
    parent_category_id = scrapy.Field(combination='1')
    # 1 - onshelf, 0 - unshelf
    category_status = scrapy.Field(combination='1')
    category_name = scrapy.Field(combination='1')
    category_url = scrapy.Field(combination='1')
    category_type = scrapy.Field(combination='1')
    category_level = scrapy.Field(combination='1')
    category_is_leaf = scrapy.Field(combination='1')

    status = scrapy.Field(status=True)
    created_time = scrapy.Field(create=True)
    deleted_time = scrapy.Field(delete=True)


class ProductPage(Product, Attribute, Sku, Market, Image):
    """
    货源网站商品详情页面信息
    """


class MarketPage(Market, Market_Attr):
    """
    货源网站市场页面信息
    """


class MarketProductPage(Market):
    """
    货源网站市场下面商品页面信息
    """


class IndexPage(Category, Market):
    """
    货源网站首页
    """


class SearchPage(Category, Market):
    """
    货源网站商品查找页面
    """


class CategoryPage(Category):
    """
    货源网站商品品类页面
    """


class ContactPage(Market):
    """
    货源网站联系页面
    """
