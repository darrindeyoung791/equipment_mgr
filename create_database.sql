-- 创建数据库
CREATE DATABASE IF NOT EXISTS equipment_mgr;
USE equipment_mgr;

-- 修改数据库字符集为 UTF-8
ALTER DATABASE equipment_mgr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 users 表
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    pswd_hash VARCHAR(255) NOT NULL,
    user_type INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    gender INT NOT NULL,
    dpt VARCHAR(100),
    title VARCHAR(100),
    status INT NOT NULL
);

-- 创建 devices 表
CREATE TABLE IF NOT EXISTS devices (
    device_id INT AUTO_INCREMENT PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    purchase_date DATE NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    status INT NOT NULL,
    lab VARCHAR(100) NOT NULL,
    can_borrow INT NOT NULL
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建 borrow_records 表
CREATE TABLE IF NOT EXISTS borrow_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    device_id INT NOT NULL,
    borrow_date DATE NOT NULL,
    return_date DATE,
    approval_status INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
);

-- 创建 approval_records 表
CREATE TABLE IF NOT EXISTS approval_records (
    approval_id INT AUTO_INCREMENT PRIMARY KEY,
    record_id INT NOT NULL,
    approver_id INT NOT NULL,
    approval_date DATE NOT NULL,
    approval_comment TEXT,
    FOREIGN KEY (record_id) REFERENCES borrow_records(record_id),
    FOREIGN KEY (approver_id) REFERENCES users(user_id)
);

-- 创建 logs 表
CREATE TABLE IF NOT EXISTS logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action INT NOT NULL,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 修改 devices 表字符集为 UTF-8
ALTER TABLE devices CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改 users 表字符集为 UTF-8
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改 borrow_records 表字符集为 UTF-8
ALTER TABLE borrow_records CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改 approval_records 表字符集为 UTF-8
ALTER TABLE approval_records CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 修改 logs 表字符集为 UTF-8
ALTER TABLE logs CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;