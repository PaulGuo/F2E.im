-- phpMyAdmin SQL Dump
-- version 3.4.10.1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2013 年 01 月 02 日 09:59
-- 服务器版本: 5.1.66
-- PHP 版本: 5.3.3

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `f2e`
--

-- --------------------------------------------------------

--
-- 表的结构 `favorite`
--

CREATE TABLE IF NOT EXISTS `favorite` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `owner_user_id` int(11) DEFAULT NULL,
  `involved_type` int(11) DEFAULT NULL,
  `involved_topic_id` int(11) DEFAULT NULL,
  `involved_reply_id` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=20 ;

-- --------------------------------------------------------

--
-- 表的结构 `node`
--

CREATE TABLE IF NOT EXISTS `node` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text,
  `slug` text,
  `thumb` text,
  `introduction` text,
  `created` text,
  `updated` text,
  `plane_id` int(11) DEFAULT NULL,
  `topic_count` int(11) DEFAULT NULL,
  `custom_style` text,
  `limit_reputation` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=41 ;

-- --------------------------------------------------------

--
-- 表的结构 `notification`
--

CREATE TABLE IF NOT EXISTS `notification` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` text,
  `status` int(11) DEFAULT NULL,
  `involved_type` int(11) DEFAULT NULL,
  `involved_user_id` int(11) DEFAULT NULL,
  `involved_topic_id` int(11) DEFAULT NULL,
  `involved_reply_id` int(11) DEFAULT NULL,
  `trigger_user_id` int(11) DEFAULT NULL,
  `occurrence_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=258 ;

-- --------------------------------------------------------

--
-- 表的结构 `plane`
--

CREATE TABLE IF NOT EXISTS `plane` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text,
  `created` text,
  `updated` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

-- --------------------------------------------------------

--
-- 表的结构 `reply`
--

CREATE TABLE IF NOT EXISTS `reply` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `topic_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `content` text,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `up_vote` int(11) DEFAULT NULL,
  `down_vote` int(11) DEFAULT NULL,
  `last_touched` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=184 ;

-- --------------------------------------------------------

--
-- 表的结构 `topic`
--

CREATE TABLE IF NOT EXISTS `topic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text,
  `content` text,
  `status` int(11) DEFAULT NULL,
  `hits` int(11) DEFAULT NULL,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `node_id` int(11) DEFAULT NULL,
  `author_id` int(11) DEFAULT NULL,
  `reply_count` int(11) DEFAULT NULL,
  `last_replied_by` text,
  `last_replied_time` datetime DEFAULT NULL,
  `up_vote` int(11) DEFAULT NULL,
  `down_vote` int(11) DEFAULT NULL,
  `last_touched` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=24 ;

--
-- 触发器 `topic`
--
DROP TRIGGER IF EXISTS `topic_delete_trigger`;
DELIMITER //
CREATE TRIGGER `topic_delete_trigger` BEFORE DELETE ON `topic`
 FOR EACH ROW BEGIN
        DELETE FROM reply WHERE reply.topic_id = OLD.id;
        DELETE FROM notification WHERE notification.involved_topic_id = OLD.id;
    END
//
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `transaction`
--

CREATE TABLE IF NOT EXISTS `transaction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` int(11) DEFAULT NULL,
  `reward` int(11) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `current_balance` int(11) DEFAULT NULL,
  `involved_user_id` int(11) DEFAULT NULL,
  `involved_topic_id` int(11) DEFAULT NULL,
  `involved_reply_id` int(11) DEFAULT NULL,
  `occurrence_time` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `user`
--

CREATE TABLE IF NOT EXISTS `user` (
  `uid` int(11) NOT NULL AUTO_INCREMENT,
  `email` text,
  `password` text,
  `username` text,
  `nickname` text,
  `avatar` text,
  `signature` text,
  `location` text,
  `website` text,
  `company` text,
  `role` int(11) DEFAULT NULL,
  `balance` int(11) DEFAULT NULL,
  `reputation` int(11) DEFAULT NULL,
  `self_intro` text,
  `created` datetime DEFAULT NULL,
  `updated` datetime DEFAULT NULL,
  `twitter` text,
  `github` text,
  `douban` text,
  `last_login` datetime DEFAULT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=171 ;

--
-- 触发器 `user`
--
DROP TRIGGER IF EXISTS `user_delete_trigger`;
DELIMITER //
CREATE TRIGGER `user_delete_trigger` BEFORE DELETE ON `user`
 FOR EACH ROW BEGIN
        DELETE FROM topic WHERE topic.author_id = OLD.uid;
        DELETE FROM reply WHERE reply.author_id = OLD.uid;
        DELETE FROM notification WHERE notification.trigger_user_id = OLD.uid;
        DELETE FROM notification WHERE notification.involved_user_id = OLD.uid;
    END
//
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `vote`
--

CREATE TABLE IF NOT EXISTS `vote` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `status` int(11) DEFAULT NULL,
  `involved_type` int(11) DEFAULT NULL,
  `involved_user_id` int(11) DEFAULT NULL,
  `involved_topic_id` int(11) DEFAULT NULL,
  `involved_reply_id` int(11) DEFAULT NULL,
  `trigger_user_id` int(11) DEFAULT NULL,
  `occurrence_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
