CREATE TABLE `article` (
  `article_id` int PRIMARY KEY AUTO_INCREMENT,
  `url` varchar(2048) NOT NULL,
  `domain_name` varchar(255) NOT NULL,
  `publication_date` timestamp,
  `title` varchar(255)
);

CREATE TABLE `gdelt` (
  `gdelt_id` int PRIMARY KEY,
  `article_id` int,
  `timestamp` datetime NOT NULL
);

CREATE TABLE `summary` (
  `article_id` int PRIMARY KEY,
  `summary` varchar(255) NOT NULL
);

CREATE TABLE `entity` (
  `entity_id` int PRIMARY KEY AUTO_INCREMENT,
  `entity` varchar(255),
  `ne_type` varchar(255)
);

CREATE TABLE `hyperlink` (
  `hyperlink_id` int PRIMARY KEY AUTO_INCREMENT,
  `hyperlink` varchar(255)
);

CREATE TABLE `date` (
  `date_id` int PRIMARY KEY AUTO_INCREMENT,
  `date` varchar(255)
);

CREATE TABLE `sentence` (
  `sentence_id` int PRIMARY KEY AUTO_INCREMENT,
  `article_id` int,
  `sentence` varchar(255),
  `sentiment_pos` float NOT NULL,
  `sentiment_neg` float NOT NULL,
  `sentiment_neu` float NOT NULL,
  `sentiment_compound` float NOT NULL
);

CREATE TABLE `sentence_entity` (
  `entity_id` int,
  `sentence_id` int,
  `frequency_in_sentence` int,
  PRIMARY KEY (`entity_id`, `sentence_id`)
);

CREATE TABLE `article_entity` (
  `article_id` int,
  `entity_id` int,
  `frequency_in_article` int,
  PRIMARY KEY (`article_id`, `entity_id`)
);

CREATE TABLE `article_date` (
  `article_id` int,
  `date_id` int,
  `frequency_in_article` int,
  PRIMARY KEY (`article_id`, `date_id`)
);

CREATE TABLE `article_hyperlink` (
  `article_id` int,
  `hyperlink_id` int,
  `frequency_in_article` int,
  PRIMARY KEY (`article_id`, `hyperlink_id`)
);

ALTER TABLE `gdelt` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `summary` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `sentence` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `sentence_entity` ADD FOREIGN KEY (`entity_id`) REFERENCES `entity` (`entity_id`);

ALTER TABLE `sentence_entity` ADD FOREIGN KEY (`sentence_id`) REFERENCES `sentence` (`sentence_id`);

ALTER TABLE `article_entity` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `article_entity` ADD FOREIGN KEY (`entity_id`) REFERENCES `entity` (`entity_id`);

ALTER TABLE `article_date` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `article_date` ADD FOREIGN KEY (`date_id`) REFERENCES `date` (`date_id`);

ALTER TABLE `article_hyperlink` ADD FOREIGN KEY (`article_id`) REFERENCES `article` (`article_id`);

ALTER TABLE `article_hyperlink` ADD FOREIGN KEY (`hyperlink_id`) REFERENCES `hyperlink` (`hyperlink_id`);

