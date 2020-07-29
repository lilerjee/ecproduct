/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50505
Source Host           : localhost:3306
Source Database       : ecproduct

Target Server Type    : MYSQL
Target Server Version : 50505
File Encoding         : 65001

Date: 2018-07-02 17:49:17
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for attribute
-- ----------------------------
DROP TABLE IF EXISTS `attribute`;
CREATE TABLE `attribute` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `product_id` char(48) DEFAULT NULL,
  `attr_name_id` int(11) unsigned DEFAULT NULL,
  `attr_name` varchar(256) NOT NULL,
  `attr_value_id` varchar(96) DEFAULT NULL,
  `attr_value` varchar(96) NOT NULL,
  `attr_value_img_url` varchar(512) DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `product_id` (`product_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE,
  KEY `attr_name_id` (`attr_name_id`) USING BTREE,
  KEY `attr_value_id` (`attr_value_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4973222 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for category
-- ----------------------------
DROP TABLE IF EXISTS `category`;
CREATE TABLE `category` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `category_id` varchar(96) NOT NULL,
  `parent_category_id` varchar(96) DEFAULT NULL,
  `category_status` smallint(6) DEFAULT NULL COMMENT '1 - onshelf, 0 - unshelf',
  `category_name` varchar(96) NOT NULL,
  `category_url` varchar(512) DEFAULT NULL,
  `category_type` varchar(48) DEFAULT NULL,
  `category_level` smallint(6) NOT NULL,
  `category_is_leaf` char(1) NOT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`platform_code`,`category_id`),
  UNIQUE KEY `id` (`id`) USING BTREE,
  KEY `category_id` (`category_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=41984 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for image
-- ----------------------------
DROP TABLE IF EXISTS `image`;
CREATE TABLE `image` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `product_id` char(48) DEFAULT NULL,
  `img_url` varchar(512) NOT NULL,
  `img_size` varchar(48) DEFAULT NULL COMMENT 'small, middle, big, large, 500x500, etc',
  `img_purpose` varchar(96) DEFAULT NULL COMMENT 'role description: index',
  `img_description` varchar(255) DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `product_id` (`product_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE,
  KEY `img_url` (`img_url`(128)) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=10531012 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for market
-- ----------------------------
DROP TABLE IF EXISTS `market`;
CREATE TABLE `market` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `market_id` varchar(96) NOT NULL COMMENT '可以人造id，用id-<number>描述属于该市场的哪个楼层或者分区',
  `parent_market_id` varchar(96) DEFAULT NULL COMMENT '市场具有层级关系，用该字段进行联系与描述',
  `market_code` varchar(48) DEFAULT NULL,
  `market_status` smallint(6) DEFAULT NULL COMMENT '1 - onshelf, 0 - unshelf',
  `market_type` varchar(48) NOT NULL COMMENT '市场类型：店铺，商场（市场），站点，楼层，区域（A区，B区)',
  `market_name` varchar(256) DEFAULT NULL,
  `market_url` varchar(512) NOT NULL,
  `related_type` varchar(48) DEFAULT NULL,
  `related_platform_code` char(5) DEFAULT NULL,
  `related_market_id` varchar(96) DEFAULT NULL,
  `related_market_url` varchar(255) DEFAULT NULL,
  `market_rank` int(11) unsigned DEFAULT NULL,
  `market_item_num` int(11) unsigned DEFAULT NULL COMMENT '市场内项目数量',
  `market_contact_wangwang` varchar(48) DEFAULT NULL,
  `market_contact_phone` varchar(48) DEFAULT NULL,
  `market_contact_weixin` varchar(48) DEFAULT NULL,
  `market_contact_qq` varchar(48) DEFAULT NULL,
  `market_contact_mail` varchar(96) DEFAULT NULL,
  `market_addr` varchar(256) DEFAULT NULL,
  `market_start_time` datetime DEFAULT NULL,
  `market_exist_time` smallint(6) DEFAULT NULL,
  `seller_id` int(11) unsigned DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`) USING BTREE,
  KEY `market_id` (`market_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=22819 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for market_attr
-- ----------------------------
DROP TABLE IF EXISTS `market_attr`;
CREATE TABLE `market_attr` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `market_id` int(11) unsigned NOT NULL,
  `market_attr_type` varchar(48) NOT NULL,
  `market_attr_name_id` int(11) unsigned DEFAULT NULL,
  `market_attr_name` varchar(256) NOT NULL,
  `market_attr_value_id` varchar(96) DEFAULT NULL,
  `market_attr_value` varchar(96) NOT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `product_id` (`market_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE,
  KEY `attr_name_id` (`market_attr_type`) USING BTREE,
  KEY `attr_value_id` (`market_attr_value_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for platform
-- ----------------------------
DROP TABLE IF EXISTS `platform`;
CREATE TABLE `platform` (
  `platform_id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `platform_name` varchar(50) NOT NULL,
  `platform_url` varchar(256) NOT NULL,
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  UNIQUE KEY `platform_id` (`platform_id`),
  UNIQUE KEY `platform_code` (`platform_code`)
) ENGINE=InnoDB AUTO_INCREMENT=386 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for product
-- ----------------------------
DROP TABLE IF EXISTS `product`;
CREATE TABLE `product` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `product_id` char(48) DEFAULT NULL,
  `market_id` varchar(96) DEFAULT NULL,
  `product_status` varchar(48) DEFAULT NULL COMMENT 'onshelf, unshelf, stockout',
  `product_name` varchar(256) DEFAULT NULL,
  `product_url` varchar(512) NOT NULL,
  `product_sale_price` decimal(15,2) DEFAULT NULL,
  `product_original_range_price` varchar(96) DEFAULT '',
  `product_range_price` varchar(96) DEFAULT '',
  `product_price_unit` char(3) DEFAULT '',
  `product_category_id` varchar(96) DEFAULT '0.00',
  `product_quantity` int(10) unsigned DEFAULT NULL,
  `product_art_no` varchar(48) DEFAULT NULL,
  `product_detail` varchar(1024) DEFAULT NULL,
  `product_img_index_url` varchar(512) DEFAULT NULL,
  `product_upload_time` datetime DEFAULT NULL,
  `product_unshelf_time` datetime DEFAULT NULL,
  `product_source_id` bigint(20) unsigned DEFAULT NULL,
  `product_source_url` varchar(512) DEFAULT NULL,
  `product_source_price` decimal(15,2) DEFAULT NULL,
  `product_source_price_unit` char(3) DEFAULT '',
  `home_item_id` int(11) unsigned DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `shop_id` (`market_id`) USING BTREE,
  KEY `home_product_id` (`home_item_id`) USING BTREE,
  KEY `product_source_id` (`product_source_id`) USING BTREE,
  KEY `product_url` (`product_url`(128)),
  KEY `platform_code` (`platform_code`),
  KEY `product_id` (`product_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=850754 DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for seller
-- ----------------------------
DROP TABLE IF EXISTS `seller`;
CREATE TABLE `seller` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `seller_id` int(11) unsigned NOT NULL,
  `seller_name` varchar(96) NOT NULL,
  `seller_url` varchar(512) DEFAULT NULL,
  `seller_contact_wangwang` varchar(48) DEFAULT NULL,
  `seller_contact_phone` varchar(48) DEFAULT NULL,
  `seller_contact_weixin` varchar(48) DEFAULT NULL,
  `seller_contact_qq` varchar(48) DEFAULT NULL,
  `seller_contact_addr` varchar(96) DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `seller_id` (`seller_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for shop
-- ----------------------------
DROP TABLE IF EXISTS `shop`;
CREATE TABLE `shop` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `shop_id` varchar(96) NOT NULL,
  `shop_name` varchar(256) NOT NULL,
  `shop_url` varchar(512) NOT NULL,
  `shop_rank` int(11) unsigned DEFAULT NULL,
  `shop_product_num` int(11) unsigned DEFAULT NULL,
  `shop_contact_wangwang` varchar(48) DEFAULT NULL,
  `shop_contact_phone` varchar(48) DEFAULT NULL,
  `shop_contact_weixin` varchar(48) DEFAULT NULL,
  `shop_contact_qq` varchar(48) DEFAULT NULL,
  `shop_contact_addr` varchar(96) DEFAULT NULL,
  `shop_contact_area` varchar(96) DEFAULT NULL,
  `seller_id` int(11) unsigned DEFAULT NULL,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`platform_code`,`shop_id`),
  UNIQUE KEY `id` (`id`) USING BTREE,
  KEY `shop_id` (`shop_id`) USING BTREE,
  KEY `platform_code` (`platform_code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for sku
-- ----------------------------
DROP TABLE IF EXISTS `sku`;
CREATE TABLE `sku` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `platform_code` char(5) NOT NULL,
  `product_id` char(48) DEFAULT NULL,
  `sku_id` varchar(24) DEFAULT '',
  `sku_key` varchar(32) DEFAULT NULL,
  `sku_value` varchar(256) NOT NULL,
  `sku_sale_count` int(11) DEFAULT NULL,
  `sku_can_book_count` int(11) DEFAULT NULL,
  `sku_price` decimal(15,2) DEFAULT 0.00,
  `status` mediumint(9) NOT NULL COMMENT 'specify the record status. 0 : created; 1+ : updated, -1 : deleted. the value of ''updated'' is the number of  update times',
  `created_time` datetime NOT NULL,
  `modified_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `deleted_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`) USING BTREE,
  KEY `product_id` (`product_id`) USING BTREE,
  KEY `sku_id` (`sku_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=6894304 DEFAULT CHARSET=utf8mb4;
