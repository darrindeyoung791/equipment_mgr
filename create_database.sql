-- 删除已存在的数据库和用户
DROP DATABASE IF EXISTS equipment_mgr;
DROP USER IF EXISTS 'equipment_admin'@'localhost';

-- 创建数据库
CREATE DATABASE equipment_mgr CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE equipment_mgr;

-- 创建用户并授权
CREATE USER 'equipment_admin'@'localhost' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON equipment_mgr.* TO 'equipment_admin'@'localhost';
FLUSH PRIVILEGES;

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
);

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

-- 插入测试用户数据
INSERT INTO users (username, pswd_hash, user_type, name, gender, dpt, title, status) VALUES
('student1', 'pbkdf2:sha256:123456', 1, '张三', 1, '计算机系', NULL, 1),
('student2', 'pbkdf2:sha256:123456', 1, '李四', 1, '物理系', NULL, 1),
('student3', 'pbkdf2:sha256:123456', 1, '王五', 2, '化学系', NULL, 1),
('teacher1', 'pbkdf2:sha256:123456', 2, '赵老师', 1, '计算机系', '副教授', 1),
('teacher2', 'pbkdf2:sha256:123456', 2, '钱老师', 2, '物理系', '教授', 1),
('admin1', 'pbkdf2:sha256:123456', 3, '孙管理', 1, '设备部', NULL, 1);

-- 插入测试设备数据
INSERT INTO devices (device_name, model, purchase_date, price, status, lab, can_borrow) VALUES
('示波器', 'OS-2102', '2023-01-01', 5000.00, 1, '电子实验室', 1),
('显微镜', 'XW-500', '2023-02-01', 3000.00, 1, '生物实验室', 1),
('服务器', 'Dell-R740', '2023-03-01', 20000.00, 1, '计算机实验室', 1),
('电子天平', 'JA2003', '2023-04-01', 8000.00, 1, '化学实验室', 1),
('光谱仪', 'SP-3000', '2023-05-01', 15000.00, 1, '物理实验室', 1),
('3D打印机', 'CR-10', '2023-06-01', 2000.00, 1, '创新实验室', 1),
('机械臂', 'UR3', '2023-07-01', 50000.00, 2, '机器人实验室', 0),
('高性能计算机', 'HP-Z8', '2023-08-01', 30000.00, 1, '计算机实验室', 1);

-- 插入一些测试借用记录
INSERT INTO borrow_records (user_id, device_id, borrow_date, return_date, approval_status) VALUES
(1, 1, '2023-05-01', '2023-05-10', 2),  -- 已归还的记录
(2, 2, '2023-05-15', NULL, 2),          -- 正在借用的记录
(3, 3, '2023-05-20', NULL, 1),          -- 待审批的记录
(1, 4, '2023-05-25', NULL, 3);          -- 被拒绝的记录

-- 插入一些测试审批记录
INSERT INTO approval_records (record_id, approver_id, approval_date, approval_comment) VALUES
(1, 4, '2023-05-01', '同意借用'),
(2, 5, '2023-05-15', '实验需要，批准使用'),
(4, 4, '2023-05-25', '设备已被预约');