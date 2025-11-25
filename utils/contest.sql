CREATE DATABASE contest DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER 'contest'@'localhost' IDENTIFIED BY 'contest';
GRANT ALL PRIVILEGES ON contest.* TO 'contest'@'localhost';
