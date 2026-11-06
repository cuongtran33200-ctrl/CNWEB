-- Chạy bằng tài khoản root của MariaDB/MySQL:
--   "C:\Program Files\MariaDB 10.11\bin\mysql.exe" -u root -p -e "source D:/cuoikycnweb/scripts/init_db.sql"

CREATE DATABASE IF NOT EXISTS blogdb
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'bloguser'@'localhost' IDENTIFIED BY 'blog_pass_123';
GRANT ALL PRIVILEGES ON blogdb.* TO 'bloguser'@'localhost';

GRANT CREATE, DROP ON *.* TO 'bloguser'@'localhost';
GRANT ALL PRIVILEGES ON `test_blogdb`.* TO 'bloguser'@'localhost';

FLUSH PRIVILEGES;