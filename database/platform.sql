/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50505
Source Host           : localhost:3306
Source Database       : ecproduct

Target Server Type    : MYSQL
Target Server Version : 50505
File Encoding         : 65001

Date: 2018-07-02 17:50:28
*/

SET FOREIGN_KEY_CHECKS=0;

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
-- Records of platform
-- ----------------------------
INSERT INTO `platform` VALUES ('1', 'JD000', 'jd', 'www.jd.com', '2019-09-26 20:02:07', '2019-09-26 20:02:07');
INSERT INTO `platform` VALUES ('2', 'AMAZO', 'amazon', 'www.amazon.com', '2019-09-26 20:02:07', '2019-09-26 20:02:07');
INSERT INTO `platform` VALUES ('3', 'WISH0', 'wish', 'www.wish.com', '2019-09-26 20:02:10', '2019-09-26 20:02:10');
INSERT INTO `platform` VALUES ('4', 'TAOBA', 'taobao', 'https://tabao.com', '2019-09-26 20:02:12', '2019-09-26 20:02:12');
INSERT INTO `platform` VALUES ('5', 'A1688', '1688', 'www.1688.com', '2019-09-26 20:02:16', '2019-09-26 20:02:16');
INSERT INTO `platform` VALUES ('6', 'TMALL', 'tmall', 'https://www.tmall.com/', '2019-09-26 20:02:24', '2019-09-26 20:02:24');
INSERT INTO `platform` VALUES ('7', 'TOOLM', 'toolmall', 'http://www.toolmall.com', '2019-09-26 20:02:24', '2019-09-26 20:02:24');
INSERT INTO `platform` VALUES ('8', 'VVIC0', 'vvic', 'http://www.vvic.com', '2019-09-26 20:02:24', '2019-09-26 20:02:24');
INSERT INTO `platform` VALUES ('9', 'WSY00', 'wsy', 'http://www.wsy.com/', '2019-09-26 20:02:25', '2019-09-26 20:02:25');
INSERT INTO `platform` VALUES ('10', 'MOGUJ', 'mogujie', 'http://www.mogujie.com/', '2019-03-12 16:37:12', '2019-03-12 16:37:17');
INSERT INTO `platform` VALUES ('11', '17HUO', '17huo', 'http://www.17huo.com/', '2019-03-12 16:38:12', '2019-03-12 16:38:17');
