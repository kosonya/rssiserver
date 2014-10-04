CREATE DATABASE `rssi_mapper_user_locations`;
USE `rssi_mapper_user_locations`;

CREATE TABLE `rssi_mapper_user_locations` (
  `timestamp` bigint(20) NOT NULL,
  `ipaddr` char(15),
  `macaddr` char(17),
  `imei` char(20),
  `lac` varchar(20),
  `latitude` double NOT NULL,
  `longitude` double NOT NULL,
  `altitude` double NOT NULL,
  `RSSI` int(11) NOT NULL,
  PRIMARY KEY (`timestamp`, `ipaddr`, `macaddr`, `imei`),
  KEY `timestamp` (`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
