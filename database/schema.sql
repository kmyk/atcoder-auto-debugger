SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `problems`;
CREATE TABLE `problems` (
    `problem_id` bigint NOT NULL AUTO_INCREMENT,
    `url` varchar(255) NOT NULL UNIQUE,
    `name` varchar(255) NOT NULL,
    PRIMARY KEY (`problem_id`)
) DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=10000;  -- NOTE: AUTO_INCREMENT starting with a random value helps debugging

DROP TABLE IF EXISTS `samples`;
CREATE TABLE `samples` (
    `problem_id` bigint NOT NULL AUTO_INCREMENT,
    `serial` tinyint unsigned NOT NULL,
    `input` blob NOT NULL,
    `output` blob NOT NULL,
    PRIMARY KEY (`problem_id`, `serial`),
    FOREIGN KEY (`problem_id`) REFERENCES `problems` (`problem_id`)
) DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `submissions`;
CREATE TABLE `submissions` (
    `submission_id` bigint NOT NULL AUTO_INCREMENT,
    `problem_id` bigint NOT NULL,
    `url` varchar(255) NOT NULL UNIQUE,
    `user` varchar(255) NOT NULL,
    `code` mediumblob NOT NULL,
    `language` varchar(255) NOT NULL,
    `status` varchar(255) NOT NULL,
    PRIMARY KEY (`submission_id`),
    FOREIGN KEY (`problem_id`) REFERENCES `problems` (`problem_id`),
    KEY `idx_url` (`url`)
) DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=20000;

DROP TABLE IF EXISTS `requests`;
CREATE TABLE `requests` (
    `request_id` bigint NOT NULL AUTO_INCREMENT,
    `submission_id` bigint NOT NULL UNIQUE,  -- NOTE: this UNIQUE constraints may be removed
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`request_id`),
    FOREIGN KEY (`submission_id`) REFERENCES `submissions` (`submission_id`)
) DEFAULT CHARSET=utf8mb4 AUTO_INCREMENT=110000;  -- NOTE: add a value to id, because too small id values discourage users

DROP TABLE IF EXISTS `jobs`;
CREATE TABLE `jobs` (
    `request_id` bigint NOT NULL,
    `ip_address` varbinary(16) NOT NULL UNIQUE,  -- NOTE: for rate restriction based on IP addresses
    `assigned_to` varchar(255) NULL DEFAULT NULL,  -- NOTE: use NULL
    `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`request_id`),
    FOREIGN KEY (`request_id`) REFERENCES `requests` (`request_id`)
) DEFAULT CHARSET=utf8mb4;

DROP TABLE IF EXISTS `results`;
CREATE TABLE `results` (
    `request_id` bigint NOT NULL,
    `data` mediumblob NOT NULL,
    `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`request_id`),
    FOREIGN KEY (`request_id`) REFERENCES `requests` (`request_id`),
    KEY `idx_created_at` (`created_at`)
) DEFAULT CHARSET=utf8mb4;
