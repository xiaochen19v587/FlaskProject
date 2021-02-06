-- MySQL dump 10.13  Distrib 5.7.33, for Linux (x86_64)
--
-- Host: localhost    Database: info
-- ------------------------------------------------------
-- Server version	5.7.33-0ubuntu0.16.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `books` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `userid` int(11) NOT NULL,
  `name` char(20) NOT NULL,
  `author` char(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_student_book` (`userid`),
  CONSTRAINT `fk_student_book` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (7,46,'钢铁是怎样炼成的','尼·奥斯特洛夫斯基'),(9,46,'西游记','吴承恩'),(10,46,'三国演义','罗贯中'),(11,48,'水浒传','施耐庵'),(12,48,'红楼梦','曹雪芹');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `carts`
--

DROP TABLE IF EXISTS `carts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `carts` (
  `userid` int(11) NOT NULL,
  `cartname` char(10) NOT NULL,
  `price` int(11) NOT NULL,
  `cartid` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`cartid`),
  KEY `users_id` (`userid`),
  CONSTRAINT `users_id` FOREIGN KEY (`userid`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `carts`
--

LOCK TABLES `carts` WRITE;
/*!40000 ALTER TABLE `carts` DISABLE KEYS */;
INSERT INTO `carts` VALUES (46,'辣条',10,44),(46,'辣条',5,46),(46,'辣条',12,47),(45,'辣条',123,48);
/*!40000 ALTER TABLE `carts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` char(20) DEFAULT NULL,
  `age` int(11) NOT NULL,
  `password` char(50) DEFAULT NULL,
  `isalive` int(11) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (32,'123',12,'3d9f0af340b84a2c3a8779ede2277e91',1),(33,'1234',23,'f30d2596e3ff16397fa5f0a231363b48',1),(35,'xiaochen',23,'a85b621f8fe765d7ec00ba2cd5d880a5',1),(36,'xiaochen19v587',23,'6573492867218b5947fdc2d6b6915b7e',1),(37,'12',23,'f424627c29c821c5b1c992d16a32683b',1),(40,'qwe',23,'59d078ddf470d4c27c91f341924e5cc1',1),(41,'4321',23,'8ec9da076be489c6fb027636d1b2e847',1),(43,'234',23,'795de1f011008bfdc4b992aa9034de9e',1),(44,'23',23,'f662f10942036a5ddbede9337b7172e5',1),(45,'zxc',23,'d916c5b386f9593373a8e38284835ed0',0),(46,'bnm',12,'2b7dcf32dba7e94931376a2f6c8bd9a6',0),(47,'hjk',12,'034e29cac24e1bdfcb9008f925d8bb6c',0),(48,'iop',12,'b0d5582c0e75b2c86fcf9f72df63df1a',0),(50,'test_',21,'b003657345d151d39f3a6496290caf5b',1),(51,'t test',21,'c5b3411c06792da0f44556981c8337cf',0),(52,'fgh',21,'36f6022965a7729725c541112c11336b',0),(53,'sdf',21,'660a6d6024dd32fc89a2f9e5ce0d80ca',0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-05 16:04:42
