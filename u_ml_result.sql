/*
 Navicat Premium Data Transfer

 Source Server         : localhost_3306
 Source Server Type    : MySQL
 Source Server Version : 50641
 Source Host           : localhost:3306
 Source Schema         : unicom_decision_test

 Target Server Type    : MySQL
 Target Server Version : 50641
 File Encoding         : 65001

 Date: 04/11/2018 11:58:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for u_ml_result
-- ----------------------------
DROP TABLE IF EXISTS `u_ml_result`;
CREATE TABLE `u_ml_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `bTypeWeight` decimal(4,4) DEFAULT '0.2500' COMMENT '[已有方案]楼宇权重',
  `bAreaWeight` decimal(4,4) DEFAULT '0.2000' COMMENT '[已有方案]单面积值权重',
  `valueZoneWeight` decimal(4,4) DEFAULT '0.1500' COMMENT '[已有方案]价值区域权重',
  `nodeWeight` decimal(4,4) DEFAULT '0.2000' COMMENT '[已有方案]单项权重',
  `complaintWeight` decimal(4,4) DEFAULT '0.1000' COMMENT '[已有方案]投诉权重',
  `customWeight` decimal(4,4) DEFAULT '0.1000' COMMENT '[已有方案]客户权重',
  `genTime` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '训练记录生成时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2522 DEFAULT CHARSET=utf8mb4 COMMENT='机器学习训练结果表，输出六个维度的权重';

-- ----------------------------
-- Records of u_ml_result
-- ----------------------------
BEGIN;
INSERT INTO `u_ml_result` VALUES (1, 0.2500, 0.2000, 0.1500, 0.2000, 0.1000, 0.1000, '2018-11-04 11:57:30');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
