-- MySQL dump 10.13  Distrib 8.0.36, for macos14 (x86_64)
--
-- Host: localhost    Database: flask_admin_panel_104
-- ------------------------------------------------------
-- Server version	5.7.31-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `addon`
--

DROP TABLE IF EXISTS `addon`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `addon` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Id',
  `title` varchar(120) NOT NULL COMMENT 'Title',
  `author` varchar(80) NOT NULL COMMENT 'Author',
  `uuid` varchar(120) NOT NULL COMMENT 'Uuid',
  `description` varchar(255) NOT NULL COMMENT 'Description',
  `version` varchar(50) NOT NULL COMMENT 'Version',
  `downloads` int(11) NOT NULL DEFAULT '0' COMMENT 'Downloads',
  `download_url` varchar(255) NOT NULL COMMENT 'Download_Url',
  `md5_hash` varchar(32) NOT NULL COMMENT 'Md5_Hash',
  `price` decimal(10,0) DEFAULT '0' COMMENT 'Price',
  `paid` smallint(6) NOT NULL DEFAULT '0' COMMENT 'Paid',
  `installed` smallint(6) NOT NULL DEFAULT '0' COMMENT 'Installed',
  `enabled` smallint(6) NOT NULL DEFAULT '1' COMMENT 'Enabled',
  `createtime` datetime NOT NULL COMMENT 'Createtime',
  `updatetime` datetime NOT NULL COMMENT 'Updatetime',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uuid` (`uuid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `addon`
--

LOCK TABLES `addon` WRITE;
/*!40000 ALTER TABLE `addon` DISABLE KEYS */;
/*!40000 ALTER TABLE `addon` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin`
--

DROP TABLE IF EXISTS `admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `group_id` int(11) NOT NULL DEFAULT '1' COMMENT 'Group Id',
  `name` varchar(20) NOT NULL COMMENT 'Username',
  `nickname` varchar(50) NOT NULL COMMENT 'Nickname',
  `password` varchar(128) DEFAULT NULL COMMENT 'Password',
  `avatar` varchar(255) DEFAULT NULL COMMENT 'Avatar',
  `email` varchar(100) NOT NULL COMMENT 'Email',
  `mobile` varchar(11) DEFAULT NULL COMMENT 'Mobile Number',
  `loginfailure` smallint(6) NOT NULL COMMENT 'Login Failure Count',
  `logintime` datetime DEFAULT NULL COMMENT 'Login Time',
  `loginip` varchar(50) DEFAULT NULL COMMENT 'Login IP',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `token` varchar(100) DEFAULT NULL COMMENT 'Session Token',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin`
--

LOCK TABLES `admin` WRITE;
/*!40000 ALTER TABLE `admin` DISABLE KEYS */;
INSERT INTO `admin` VALUES (1,1,'admin','Admin','$2b$12$jHxeLVMfMrK5mg/rs05WOuJjwLsIvJlKUY6tAgxNOzfhbmCaCBdhW','/static/uploads/20240507/c48188c0-286d-493c-8649-71ce4aef475a.jpg','admin@admin.com','',0,'2024-03-05 01:34:35','27.30.110.110','2024-03-05 02:32:30','2024-05-07 09:39:14','','normal');
/*!40000 ALTER TABLE `admin` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_group`
--

DROP TABLE IF EXISTS `admin_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `pid` int(11) NOT NULL COMMENT 'Parent Group',
  `name` varchar(100) NOT NULL COMMENT 'Group Name',
  `rules` varchar(500) NOT NULL COMMENT 'Rule IDs',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_group`
--

LOCK TABLES `admin_group` WRITE;
/*!40000 ALTER TABLE `admin_group` DISABLE KEYS */;
INSERT INTO `admin_group` VALUES (1,0,'admin','*','2024-04-05 12:15:11','2024-04-05 12:15:11','normal'),(2,2,'editor','1,2','2024-04-05 12:15:38','2024-04-05 13:59:18','normal');
/*!40000 ALTER TABLE `admin_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_log`
--

DROP TABLE IF EXISTS `admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `admin_id` int(11) NOT NULL COMMENT 'Administrator ID',
  `username` varchar(30) NOT NULL COMMENT 'Administrator Name',
  `url` varchar(1500) NOT NULL COMMENT 'Operated Page',
  `title` varchar(100) DEFAULT NULL COMMENT 'Log Title',
  `content` text NOT NULL COMMENT 'Content',
  `ip` varchar(50) NOT NULL COMMENT 'IP Address',
  `useragent` varchar(255) DEFAULT NULL COMMENT 'User Agent',
  `createtime` datetime DEFAULT NULL COMMENT 'Operation Time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_log`
--

LOCK TABLES `admin_log` WRITE;
/*!40000 ALTER TABLE `admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `admin_rule`
--

DROP TABLE IF EXISTS `admin_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_rule` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `type` enum('menu','action') NOT NULL COMMENT 'Type',
  `pid` int(11) NOT NULL COMMENT 'PARENT ID',
  `addon` smallint(6) NOT NULL COMMENT 'From Addon',
  `name` varchar(150) NOT NULL COMMENT 'Route Name',
  `url_path` varchar(50) NOT NULL COMMENT 'Url_Path',
  `title` varchar(50) NOT NULL COMMENT 'Title',
  `description` varchar(500) DEFAULT NULL COMMENT 'Description',
  `icon` varchar(50) DEFAULT NULL COMMENT 'Icon',
  `menutype` enum('addtabs','blank','dialog','ajax') DEFAULT NULL COMMENT 'Menutype',
  `extend` varchar(255) DEFAULT NULL COMMENT 'Extend',
  `createtime` datetime DEFAULT NULL COMMENT 'Createtime',
  `updatetime` datetime DEFAULT NULL COMMENT 'Updatetime',
  `weigh` int(11) NOT NULL COMMENT 'Weigh',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_rule`
--

LOCK TABLES `admin_rule` WRITE;
/*!40000 ALTER TABLE `admin_rule` DISABLE KEYS */;
INSERT INTO `admin_rule` VALUES (1,'menu',0,0,'admin.dashboard','/admin/dashboard','Dashboard','None','ti ti-dashboard','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',1,'normal'),(2,'menu',0,0,'admin.generals','/admin/generals','Generals','None','ti ti-settings','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',2,'normal'),(3,'menu',2,0,'admin.general.profile','/admin/general/profile','Profile','None','ti ti-user','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',11,'normal'),(4,'action',3,0,'admin.general.profile.save','/admin/general/profile/save','Save','','','blank','None','2024-01-22 14:32:00','2024-01-22 14:32:00',34,'normal'),(5,'menu',2,0,'admin.general.category','/admin/general/category','Category','None','ti ti-leaf','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',7,'normal'),(6,'action',6,0,'admin.general.category.add','/admin/general/category/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',27,'normal'),(7,'action',6,0,'admin.general.category.edit','/admin/general/category/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',28,'normal'),(8,'action',6,0,'admin.general.category.save','/admin/general/category/save','Save','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',28,'normal'),(9,'action',6,0,'admin.general.category.delete','/admin/general/category/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',29,'normal'),(10,'menu',2,0,'admin.general.config','/admin/general/config','Config','None','ti ti-cog','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',8,'normal'),(11,'action',10,0,'admin.general.config.add','/admin/general/config/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',32,'normal'),(12,'action',10,0,'admin.general.config.save','/admin/general/config/save','Save','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',33,'normal'),(13,'action',10,0,'admin.general.config.delete','/admin/general/config/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',34,'normal'),(14,'action',10,0,'admin.general.config.table.list','/admin/general/config/table/list','Table List','None','None','addtabs','None','2024-04-02 11:51:00','2024-04-02 11:51:00',0,'normal'),(15,'menu',0,0,'admin.attachment','/admin/attachment/','Attachment','None','ti ti-paperclip','blank','None','2024-01-22 14:32:00','2024-01-22 14:32:00',9,'normal'),(16,'menu',15,0,'admin.attachment.image','/admin/attachment/image','Attachment Image','None','ti ti-file-image-o','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',9,'normal'),(17,'action',16,0,'admin.attachment.image.add','/admin/attachment/image/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',35,'normal'),(18,'action',16,0,'admin.attachment.image.edit','/admin/attachment/image/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',36,'normal'),(19,'action',16,0,'admin.attachment.image.save','/admin/attachment/image/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',37,'normal'),(20,'action',16,0,'admin.attachment.image.delete','/admin/attachment/image/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',37,'normal'),(21,'menu',15,0,'admin.attachment.file','/admin/attachment/file','Attachment File','None','ti ti-file-image-o','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',10,'normal'),(22,'action',21,0,'admin.attachment.file.add','/admin/attachment/file/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',38,'normal'),(23,'action',21,0,'admin.attachment.file.edit','/admin/attachment/file/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',39,'normal'),(24,'action',21,0,'admin.attachment.file.save','/admin/attachment/file/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',40,'normal'),(25,'action',21,0,'admin.attachment.file.delete','/admin/attachment/file/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',40,'normal'),(26,'menu',0,0,'admin.addon','/admin/addon','Addon','Addon Marketplace','ti ti-rocket','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',3,'normal'),(27,'action',26,0,'admin.addon.state','/admin/addon/state','Update state','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',16,'normal'),(28,'action',26,0,'admin.addon.config','/admin/addon/config','Setting','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',17,'normal'),(29,'action',26,0,'admin.addon.refresh','/admin/addon/refresh','Refresh','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',18,'normal'),(30,'action',26,0,'admin.addon.multi','/admin/addon/multi','Multi','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',19,'normal'),(31,'action',26,0,'admin.addon.install','/admin/addon/install','Install','','','blank','None','2024-01-22 14:32:00','2024-01-22 14:32:00',16,'normal'),(32,'action',26,0,'admin.addon.uninstall','/admin/addon/uninstall','Uninstall','','','blank','None','2024-01-22 14:32:00','2024-01-22 14:32:00',16,'normal'),(33,'action',26,0,'admin.addon.update.status','/admin/addon/update/status','Update status','','','blank','None','2024-03-08 09:00:00','2024-03-08 09:00:00',0,'normal'),(34,'action',26,0,'admin.addon.download','/admin/addon/download','Download','','','blank','None','2024-03-14 09:18:00','2024-03-14 09:18:00',0,'normal'),(35,'menu',0,0,'admin.admin','/admin','Admin','None','ti ti-adjustments-alt','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',4,'normal'),(36,'menu',35,0,'admin.admin2','/admin/admin','Admin Manage','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',20,'normal'),(37,'action',37,0,'admin.admin.add','/admin/admin/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',41,'normal'),(38,'action',37,0,'admin.admin.edit','/admin/admin/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',42,'normal'),(39,'action',37,0,'admin.admin.save','/admin/admin/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',43,'normal'),(40,'action',37,0,'admin.admin.delete','/admin/admin/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',43,'normal'),(41,'menu',35,0,'admin.admin.group','/admin/admin/group','Admin Group','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',21,'normal'),(42,'action',41,0,'admin.admin.group.add','/admin/admin/group/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',44,'normal'),(43,'action',41,0,'admin.admin.group.edit','/admin/admin/group/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',45,'normal'),(44,'action',41,0,'admin.admin.group.save','/admin/admin/group/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',46,'normal'),(45,'action',41,0,'admin.admin.group.delete','/admin/admin/group/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',46,'normal'),(46,'menu',35,0,'admin.admin.rule','/admin/admin/rule','Admin Rule','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',47,'normal'),(47,'action',47,0,'admin.admin.rule.add','/admin/admin/rule/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',47,'normal'),(48,'action',47,0,'admin.admin.rule.edit','/admin/admin/rule/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',48,'normal'),(49,'action',47,0,'admin.admin.rule.save','/admin/admin/rule/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',49,'normal'),(50,'action',47,0,'admin.admin.rule.delete','/admin/admin/rule/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',49,'normal'),(51,'menu',35,0,'admin.admin.log','/admin/admin/log','Admin Log','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',50,'normal'),(52,'action',51,0,'admin.admin.log.delete','/admin/admin/log/delete','Delete','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',51,'normal'),(53,'menu',0,0,'admin.users','/admin/users','User Manage','None','ti ti-user','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',24,'normal'),(54,'menu',53,0,'admin.user','/admin/user','User Manage','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',24,'normal'),(55,'action',54,0,'admin.user.add','/admin/user/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',54,'normal'),(56,'action',54,0,'admin.user.edit','/admin/user/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',53,'normal'),(57,'action',54,0,'admin.user.save','/admin/user/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',55,'normal'),(58,'action',54,0,'admin.user.delete','/admin/user/delete','Del','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',55,'normal'),(59,'menu',53,0,'admin.user.group','/admin/user/group','User Group','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',25,'normal'),(60,'action',59,0,'admin.user.group.add','/admin/user/group/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',56,'normal'),(61,'action',59,0,'admin.user.group.edit','/admin/user/group/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',57,'normal'),(62,'action',59,0,'admin.user.group.save','/admin/user/group/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',58,'normal'),(63,'action',59,0,'admin.user.group.delete','/admin/user/group/delete','Del','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',58,'normal'),(64,'menu',53,0,'admin.user.rule','/admin/user/rule','User Rule','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',26,'normal'),(65,'action',65,0,'admin.user.rule.add','/admin/user/rule/add','Add','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',61,'normal'),(66,'action',65,0,'admin.user.rule.edit','/admin/user/rule/edit/{id}','Edit','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',62,'normal'),(67,'action',65,0,'admin.user.rule.save','/admin/user/rule/save','Save','None','None','addtabs','None','2024-01-23 14:32:00','2024-01-23 14:32:00',63,'normal'),(68,'action',65,0,'admin.user.rule.delete','/admin/user/rule/delete','Del','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',60,'normal'),(69,'menu',53,0,'admin.user.balance.log','/admin/user/balance/log','User Balance Log','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',25,'normal'),(70,'action',69,0,'admin.user.balance.log.delete','/admin/user/balance/log/delete','Del','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',58,'normal'),(71,'menu',53,0,'admin.user.score.log','/admin/user/score/log','User Score Log','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',25,'normal'),(72,'action',71,0,'admin.user.score.log.delete','/admin/user/score/log/delete','Del','None','None','addtabs','None','2024-01-22 14:32:00','2024-01-22 14:32:00',58,'normal');
/*!40000 ALTER TABLE `admin_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('adf34ccc9860');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attachment_file`
--

DROP TABLE IF EXISTS `attachment_file`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attachment_file` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `category` varchar(50) DEFAULT NULL COMMENT 'GeneralCategory',
  `admin_id` int(11) NOT NULL COMMENT 'Administrator ID',
  `user_id` int(11) NOT NULL COMMENT 'Member ID',
  `path_file` varchar(255) NOT NULL COMMENT 'Physical Path',
  `file_name` varchar(100) DEFAULT NULL COMMENT 'File Name',
  `file_size` int(11) NOT NULL COMMENT 'File Size',
  `mimetype` varchar(100) DEFAULT NULL COMMENT 'MIME Type',
  `extparam` varchar(255) DEFAULT NULL COMMENT 'Passthrough Data',
  `createtime` datetime NOT NULL COMMENT 'Createtime',
  `updatetime` datetime NOT NULL COMMENT 'Update Time',
  `storage` varchar(100) NOT NULL COMMENT 'Storage Location',
  `sha1` varchar(40) DEFAULT NULL COMMENT 'SHA1 Hash of the File',
  `general_attachmentcol` varchar(45) DEFAULT NULL COMMENT 'General Attachmentcol',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachment_file`
--

LOCK TABLES `attachment_file` WRITE;
/*!40000 ALTER TABLE `attachment_file` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachment_file` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attachment_image`
--

DROP TABLE IF EXISTS `attachment_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attachment_image` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `category` varchar(50) DEFAULT NULL COMMENT 'GeneralCategory',
  `admin_id` int(11) NOT NULL COMMENT 'Administrator ID',
  `user_id` int(11) NOT NULL COMMENT 'Member ID',
  `path_image` varchar(255) NOT NULL COMMENT 'Physical Path',
  `image_width` varchar(30) DEFAULT NULL COMMENT 'Image Width',
  `image_height` varchar(30) DEFAULT NULL COMMENT 'Image Height',
  `image_type` varchar(30) DEFAULT NULL COMMENT 'Image Type',
  `name` varchar(100) NOT NULL COMMENT 'File Name',
  `file_size` int(11) NOT NULL COMMENT 'File Size',
  `mimetype` varchar(100) DEFAULT NULL COMMENT 'MIME Type',
  `extparam` varchar(255) DEFAULT NULL COMMENT 'Passthrough Data',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `storage` varchar(100) DEFAULT NULL COMMENT 'Storage Location',
  `sha1` varchar(40) DEFAULT NULL COMMENT 'SHA1 Hash of the File',
  `general_attachmentcol` varchar(45) DEFAULT NULL COMMENT 'General Attachmentcol',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attachment_image`
--

LOCK TABLES `attachment_image` WRITE;
/*!40000 ALTER TABLE `attachment_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `attachment_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `common_ems`
--

DROP TABLE IF EXISTS `common_ems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_ems` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `event` varchar(30) DEFAULT NULL COMMENT 'Event',
  `email` varchar(100) DEFAULT NULL COMMENT 'Email Address',
  `code` varchar(10) DEFAULT NULL COMMENT 'Verification Code',
  `times` int(11) NOT NULL COMMENT 'Validation Attempts',
  `ip` varchar(30) DEFAULT NULL COMMENT 'IP Address',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_ems`
--

LOCK TABLES `common_ems` WRITE;
/*!40000 ALTER TABLE `common_ems` DISABLE KEYS */;
/*!40000 ALTER TABLE `common_ems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `common_sms`
--

DROP TABLE IF EXISTS `common_sms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_sms` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `event` varchar(30) DEFAULT NULL COMMENT 'Event',
  `mobile` varchar(20) DEFAULT NULL COMMENT 'Phone Number',
  `code` varchar(10) DEFAULT NULL COMMENT 'Verification Code',
  `times` int(11) NOT NULL COMMENT 'Validation Attempts',
  `ip` varchar(30) DEFAULT NULL COMMENT 'IP Address',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `common_sms`
--

LOCK TABLES `common_sms` WRITE;
/*!40000 ALTER TABLE `common_sms` DISABLE KEYS */;
/*!40000 ALTER TABLE `common_sms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `general_category`
--

DROP TABLE IF EXISTS `general_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `general_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `pid` int(11) NOT NULL COMMENT 'Parent ID',
  `type` varchar(30) NOT NULL COMMENT 'GeneralCategory Type',
  `name` varchar(30) NOT NULL COMMENT 'Name',
  `image` varchar(100) DEFAULT NULL COMMENT 'Image',
  `keywords` varchar(255) DEFAULT NULL COMMENT 'Keywords',
  `description` varchar(255) DEFAULT NULL COMMENT 'Description',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `weigh` int(11) NOT NULL COMMENT 'Weight',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `general_category`
--

LOCK TABLES `general_category` WRITE;
/*!40000 ALTER TABLE `general_category` DISABLE KEYS */;
INSERT INTO `general_category` VALUES (7,0,'default','default','','','','2024-05-08 17:19:06','2024-05-08 17:19:06',0,'normal');
/*!40000 ALTER TABLE `general_category` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `general_config`
--

DROP TABLE IF EXISTS `general_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `general_config` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(30) NOT NULL COMMENT 'Variable Name',
  `group` varchar(30) NOT NULL COMMENT 'Group',
  `title` varchar(100) NOT NULL COMMENT 'Variable Title',
  `tip` varchar(100) DEFAULT NULL COMMENT 'Variable Description',
  `type` varchar(30) DEFAULT NULL COMMENT 'Type: string, text, int, bool, array, datetime, date, file',
  `visible` varchar(255) DEFAULT NULL COMMENT 'Visibility Condition',
  `value` text COMMENT 'Variable Value',
  `content` text COMMENT 'Variable Dictionary Data',
  `rule` varchar(100) DEFAULT NULL COMMENT 'Validation Rule',
  `extend` varchar(255) DEFAULT NULL COMMENT 'Extended Attributes',
  `setting` varchar(255) DEFAULT NULL COMMENT 'Settings',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `general_config`
--

LOCK TABLES `general_config` WRITE;
/*!40000 ALTER TABLE `general_config` DISABLE KEYS */;
INSERT INTO `general_config` VALUES (1,'name','basic','Site name','Please Input  Site name','string','','栈鱼后台管理系统1.0','','required','',''),(2,'copyright','basic','Copyright','Please Input  Copyright','string','','Copyright © 2024 <a href=\"https://admin-panel.zhanor.com\" class=\"link-secondary\">栈鱼后台管理系统 1.0</a>. All rights reserved.','','','',''),(3,'cdnurl','basic','Cdn url','Please Input  Site name','string','','https://zhanor.com','','','',''),(4,'version','basic','Version','Please Input  Version','string','','1.0.1','','required','',''),(5,'timezone','basic','Timezone','','string','','Asia/Shanghai','','required','',''),(6,'forbiddenip','basic','Forbidden ip','Please Input  Forbidden ip','text','','12.23.21.1  1.2.3.6','','','',''),(7,'languages','basic','Languages','','array','','{\"backend\": \"zh-cn\", \"frontend\": \"zh-cn\"}','','required','',''),(8,'fixedpage','basic','Fixed page','Please Input Fixed page','string','','dashboard','','required','',''),(9,'categorytype','dictionary','Category type','','array','','{\"default\": \"Default\", \"page\": \"Page\", \"article\": \"Article\"}','','','',''),(11,'mail_type','email','Mail type','Please Input Mail type','select','','0','[\"Please Select\",\"SMTP\"]','','',''),(12,'mail_smtp_host','email','Mail smtp host','Please Input Mail smtp host','string','','smtp.qq.com','','','',''),(13,'mail_smtp_port','email','Mail smtp port','Please Input  Mail smtp port(default25,SSL：465,TLS：587)','string','','465','','','',''),(14,'mail_smtp_user','email','Mail smtp user','Please Input Mail smtp user','string','','10000','','','',''),(15,'mail_smtp_pass','email','Mail smtp password','Please Input  Mail smtp password','string','','password','','','',''),(16,'mail_verify_type','email','Mail vertify type','Please Input Mail vertify type','select','','0','[\"None\",\"TLS\",\"SSL\"]','','',''),(17,'mail_from','email','Mail from','','string','','10000@qq.com','','','',''),(18,'image_category','dictionary','Attachment Image category','','array','','{\"default\": \"Default\", \"upload\": \"Upload\"}','','','',''),(19,'file_category','dictionary','Attachment File category','','array','','{\"default\": \"Default\", \"upload\": \"Upload\"}','','','',''),(23,'user_page_title','user','User Page Title','User Page Title','text','','Member Center','','letters','',''),(24,'user_footer','user','User Center Footer','User Center Footer','string','','Copyright © 2024 <a href=\"https://admin-panel.zhanor.com\" class=\"link-secondary\">会员中心</a>. All rights reserved.','','required','','');
/*!40000 ALTER TABLE `general_config` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_group_id` int(11) NOT NULL COMMENT 'Group ID',
  `name` varchar(32) NOT NULL COMMENT 'Username',
  `nickname` varchar(50) NOT NULL COMMENT 'Nickname',
  `password` varchar(120) NOT NULL COMMENT 'Password',
  `email` varchar(100) NOT NULL COMMENT 'Email',
  `mobile` varchar(16) NOT NULL COMMENT 'Mobile Phone Number',
  `avatar` varchar(255) DEFAULT NULL COMMENT 'Avatar',
  `level` smallint(6) NOT NULL COMMENT 'Level',
  `gender` enum('female','male') NOT NULL COMMENT 'Gender',
  `birthday` date DEFAULT NULL COMMENT 'Date of Birth',
  `bio` varchar(100) DEFAULT NULL COMMENT 'Motto',
  `balance` decimal(10,0) DEFAULT NULL COMMENT 'Balance',
  `score` int(11) NOT NULL COMMENT 'Points',
  `successions` int(11) NOT NULL COMMENT 'Consecutive Login Days',
  `maxsuccessions` int(11) NOT NULL COMMENT 'Maximum Consecutive Login Days',
  `prevtime` datetime DEFAULT NULL COMMENT 'Previous Login Time',
  `logintime` datetime DEFAULT NULL COMMENT 'Login Time',
  `loginip` varchar(50) DEFAULT NULL COMMENT 'Login IP Address',
  `loginfailure` smallint(6) NOT NULL COMMENT 'Failed Login Attempts',
  `joinip` varchar(50) DEFAULT NULL COMMENT 'Joining IP Address',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `verification` varchar(255) DEFAULT NULL COMMENT 'Verification',
  `token` varchar(50) DEFAULT NULL COMMENT 'Token',
  `status` enum('normal','hidden') DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `mobile` (`mobile`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,1,'user1','user1','$2b$12$Qh2TzcECJH80i.xD/72vZO2zibNJviV4eTJ4HDT7lXK9MJlqWdpFy','user1@user.com','18811118888','static/img/avator.png',0,'male','2024-04-16','',0,0,1,1,'2024-04-16 10:22:07','2024-04-16 10:43:52','127.0.0.1',1,'127.0.0.1','2024-04-16 10:22:07','2024-04-16 10:22:07','0','','normal');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_balance_log`
--

DROP TABLE IF EXISTS `user_balance_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_balance_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) NOT NULL COMMENT 'Member ID',
  `balance` decimal(10,0) NOT NULL COMMENT 'Change in Balance',
  `before` decimal(10,0) NOT NULL COMMENT 'Balance Before Change',
  `after` decimal(10,0) NOT NULL COMMENT 'Balance After Change',
  `memo` varchar(255) DEFAULT NULL COMMENT 'Memo/Note',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_balance_log`
--

LOCK TABLES `user_balance_log` WRITE;
/*!40000 ALTER TABLE `user_balance_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_balance_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_group`
--

DROP TABLE IF EXISTS `user_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `name` varchar(50) DEFAULT NULL COMMENT 'Group Name',
  `rules` varchar(512) DEFAULT NULL COMMENT 'Permission Nodes',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `status` enum('normal','hidden') NOT NULL DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_group`
--

LOCK TABLES `user_group` WRITE;
/*!40000 ALTER TABLE `user_group` DISABLE KEYS */;
INSERT INTO `user_group` VALUES (1,'default','1,2','2024-03-27 07:37:07','2024-03-27 07:37:07','normal'),(3,'vip1','1,2','2024-03-27 15:40:57','2024-03-27 15:40:57','normal');
/*!40000 ALTER TABLE `user_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_recharge_order`
--

DROP TABLE IF EXISTS `user_recharge_order`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_recharge_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `trade_no` varchar(100) DEFAULT NULL COMMENT 'Trade No',
  `user_id` int(11) DEFAULT NULL COMMENT 'User ID',
  `amount` decimal(10,0) DEFAULT NULL COMMENT 'amount',
  `pay_amount` int(11) DEFAULT NULL COMMENT 'Pay Amount',
  `transaction_id` varchar(120) DEFAULT NULL COMMENT 'Transaction_Id',
  `payment_method` varchar(50) DEFAULT NULL COMMENT 'Payment Method',
  `pay_time` datetime DEFAULT NULL COMMENT 'Pay Time',
  `ip` varchar(50) DEFAULT NULL COMMENT 'IP',
  `useragent` varchar(255) DEFAULT NULL COMMENT 'UserAgent',
  `memo` varchar(255) DEFAULT NULL COMMENT 'Memo',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time ',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `status` enum('created','paid','expired') DEFAULT 'created' COMMENT 'Status',
  PRIMARY KEY (`id`),
  UNIQUE KEY `trade_no` (`trade_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_recharge_order`
--

LOCK TABLES `user_recharge_order` WRITE;
/*!40000 ALTER TABLE `user_recharge_order` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_recharge_order` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_rule`
--

DROP TABLE IF EXISTS `user_rule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_rule` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `pid` int(11) NOT NULL COMMENT 'Parent ID',
  `type` enum('menu','action') NOT NULL COMMENT 'Type',
  `name` varchar(100) NOT NULL COMMENT 'Route Name',
  `url_path` varchar(150) NOT NULL COMMENT 'Url Path',
  `title` varchar(50) NOT NULL COMMENT 'Title',
  `icon` varchar(45) DEFAULT NULL COMMENT 'Icon',
  `description` varchar(100) DEFAULT NULL COMMENT 'Description',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  `updatetime` datetime DEFAULT NULL COMMENT 'Update Time',
  `weigh` int(11) DEFAULT NULL COMMENT 'Weight',
  `status` enum('normal','hidden') DEFAULT 'normal' COMMENT 'Status',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_rule`
--

LOCK TABLES `user_rule` WRITE;
/*!40000 ALTER TABLE `user_rule` DISABLE KEYS */;
INSERT INTO `user_rule` VALUES (1,0,'menu','user.dashboard','/user/dashboard','User Dashboard','ti ti-hexagonal-prism','User Dashboard','2024-04-01 09:53:30','2024-04-01 15:19:07',1,'normal'),(2,0,'menu','user.profile','/user/profile','Profile','ti ti-alert-square-rounded','','2024-04-01 10:08:49','2024-04-01 12:50:48',0,'normal'),(3,0,'menu','user.balance.log','/user/balance/log','Balance Log','ti ti-color-swatch','','2024-04-01 10:09:32','2024-04-01 13:11:04',0,'normal'),(4,0,'menu','user.score.log','/user/score/log','Score Log','ti ti-align-right','','2024-04-01 10:10:03','2024-04-01 13:17:28',0,'normal'),(5,0,'action','user.logout','/user/logout','Logout','ti ti-location-share','','2024-04-01 10:11:22','2024-04-01 13:17:42',0,'normal'),(6,2,'action','user.profile.save','/user/profile/save','Profile Save','','','2024-04-01 10:21:23','2024-04-01 10:21:23',0,'normal');
/*!40000 ALTER TABLE `user_rule` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_score_log`
--

DROP TABLE IF EXISTS `user_score_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_score_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `user_id` int(11) NOT NULL COMMENT 'Member ID',
  `score` int(11) NOT NULL COMMENT 'Change in Scores',
  `before` int(11) NOT NULL COMMENT 'Points Before Change',
  `after` int(11) NOT NULL COMMENT 'Points After Change',
  `memo` varchar(255) DEFAULT NULL COMMENT 'Memo/Note',
  `createtime` datetime DEFAULT NULL COMMENT 'Creation Time',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_score_log`
--

LOCK TABLES `user_score_log` WRITE;
/*!40000 ALTER TABLE `user_score_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `user_score_log` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-06-24 11:29:59
