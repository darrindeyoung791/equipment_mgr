# 实验设备管理系统（MySQL+Flask）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于管理实验设备的系统。使用MySQL数据库、Flask后端以及基于HTML、CSS和JavaScript构建的轻量级Web界面。能够实现多角色用户管理、设备按条件查询与操作、完成操作发送通知、审批等功能。网页适配各尺寸屏幕的显示。

## Contributors

| <img src="https://avatars.githubusercontent.com/u/205942924?v=4" style="zoom:23%;" /> | [darrindeyoung791](https://github.com/darrindeyoung791) | 项目发起者，组长；<br />数据库结构设计；<br />网页界面设计；<br />版本管理；<br />文档维护。 |
| :----------------------------------------------------------: | ------------------------------------------------------- | ------------------------------------------------------------ |
| <img src="https://avatars.githubusercontent.com/u/155410580?s=130&v=4" style="zoom:25%;" /> | [ying8502](https://github.com/ying8502)                 | 参与者；<br />数据库结构设计；<br />网页架构设计。           |
| <img src="https://avatars.githubusercontent.com/u/214098553?s=130&v=4" style="zoom:25%;" /> | [Frozentime3](https://github.com/Frozentime3)           | 参与者；<br />资料搜集；<br />文档维护。                     |



## 预定功能

1. 用户管理模块
    1. 多类型用户：
        - 学生、~~教师~~、管理员
        - 注册与登录
        
    2. 密码存储：加密存储，数据库存储哈希值而非明文
    
    3. 用户信息管理（to do）：
        - 学生可以更新密码、联系方式、专业等，不可变更ID、性别
        
            > - ~~教师可以更新密码、联系方式、职称等，不可变更ID、性别~~
        
        - 管理员可以按条件删除学生账号（例如毕业生）、~~删除教师账号（例如离职教师）~~、变更数据（例如转专业的学生）
    
2. 设备管理模块（to do）
    > 1. ~~录入新设备：~~
    >     - ~~设备名称、型号、购入时间、价格、状态（正常/需要维修/维修中/报废）、所属实验室（例如大数据实验室、化学实验室）、能否借用（是/否）等~~
    > 2. ~~查询设备：~~
    >     - ~~按上述字段查询设备~~
    > 3. ~~编辑设备信息：~~
    >     - ~~例如维修时，能否借用项需要置否，状态更改为维修中~~
    >     - ~~报废的设备需要删除~~
    >     - ~~此项必须由教师或管理员更改，学生无权更改~~
    
    - 编辑设备（新建/删除与编辑已有）：
    
        - 要编辑一个设备，需要先查找，再编辑
    
        - 设备名称、型号、购入时间、价格、状态（正常/需要维修/维修中/报废）、所属实验室（例如大数据实验室、化学实验室）、能否借用（是/否）等
        - 新建/编辑/移除
    
3. 设备借还模块（借还状态需要记载于另一单独表下）：
    - 学生申请使用
    - ~~教师~~管理员审批
    - 学生归还（不经过审批）
    
4. 通知系统：
    - 借用申请审批结果通知
    
    - 设备归还提醒
    
    - 设备维修完成通知

## 数据库设计

### 1. `users` 表

> 存放全部用户数据

```plaintext
user_id          INT AUTO_INCREMENT PRIMARY KEY, -- 用户唯一标识
username         VARCHAR(50) NOT NULL,           -- 用户名，用于登录
pswd_hash        VARCHAR(255) NOT NULL,          -- 加密后的密码哈希值
user_type        INT NOT NULL,                   -- 用户类型（1: 学生, 2: 教师, 3: 管理员）
name             VARCHAR(100) NOT NULL,          -- 用户姓名
gender           INT NOT NULL,                   -- 性别（1: 男, 2: 女）
dpt              VARCHAR(100),                   -- 所属院系或专业
title            VARCHAR(100),                   -- 职称
status           INT NOT NULL                    -- 用户状态（1: 正常, 2: 毕业, 3: 离职等）
```

### 2. `devices` 表

> 存放全部设备数据

```plaintext
device_id        INT AUTO_INCREMENT PRIMARY KEY, -- 设备唯一标识
device_name      VARCHAR(100) NOT NULL,          -- 设备名称
model            VARCHAR(100) NOT NULL,          -- 设备型号
purchase_date    DATE NOT NULL,                  -- 购入时间
price            DECIMAL(10, 2) NOT NULL,        -- 设备价格
status           INT NOT NULL,                   -- 设备状态（1: 正常, 2: 需要维修, 3: 维修中, 4: 报废）
lab              VARCHAR(100) NOT NULL,          -- 所属实验室
can_borrow       INT NOT NULL                    -- 是否可以借用（1: 是, 0: 否）
```

### 3. `borrow_records` 表

> 借用记录表

```plaintext
record_id        INT AUTO_INCREMENT PRIMARY KEY, -- 借还记录唯一标识
user_id          INT NOT NULL,                   -- 借用人ID，关联到`users`表
device_id        INT NOT NULL,                   -- 借用设备ID，关联到`devices`表
borrow_date      DATE NOT NULL,                  -- 借用日期
return_date      DATE,                           -- 归还日期，如果尚未归还则为NULL
return_deadline  DATE,                           -- 归还截止日期
approval_status  INT NOT NULL                    -- 审批状态（1: 待审批, 2: 已批准, 3: 已拒绝）
approver_id      INT,                            -- 审批人ID，关联到`users`表
```

### 4. `approval_records` 表

> 审批记录表

```plaintext
approval_id      INT AUTO_INCREMENT PRIMARY KEY, -- 审批记录唯一标识
record_id        INT NOT NULL,                   -- 关联到`borrow_records`表的借还记录ID
approver_id      INT NOT NULL,                   -- 审批人ID，关联到`users`表
approval_date    DATE NOT NULL,                  -- 审批日期
approval_comment TEXT                            -- 审批意见，如拒绝原因等
```

### 5. `logs` 表

> 日志表，可能可以不设计

```plaintext
log_id           INT AUTO_INCREMENT PRIMARY KEY, -- 日志记录唯一标识
user_id          INT NOT NULL,                   -- 操作用户ID，关联到`users`表
action           INT NOT NULL,                   -- 操作类型（1: 设备更新, 2: 用户删除等）
details          TEXT,                           -- 操作详情，如具体更新了哪些字段
timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- 操作发生的时间
```

### 6. `notifications` 表

> 存放系统通知

```plaintext
notification_id  INT AUTO_INCREMENT PRIMARY KEY, -- 通知唯一标识
user_id          INT NOT NULL,                   -- 接收通知的用户ID
type            INT NOT NULL,                    -- 通知类型（1: 审批通过, 2: 审批拒绝, 3: 归还提醒, 4: 维修完成）
content         TEXT NOT NULL,                   -- 通知内容
related_id      INT,                            -- 相关记录ID（如借用记录ID）
created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- 通知创建时间
read_status     INT NOT NULL DEFAULT 0,         -- 阅读状态（0: 未读, 1: 已读）
FOREIGN KEY (user_id) REFERENCES users(user_id)
```


## ER 图

```mermaid
erDiagram
    User ||--o{ BorrowRecord : borrows
    User ||--o{ Notification : receives
    User ||--o{ ApprovalRecord : approves
    User ||--o{ Log : logs
    Device ||--o{ BorrowRecord : borrowed_in
    Device ||--o{ ApprovalRecord : approved_for
    BorrowRecord ||--o{ ApprovalRecord : has_approval
    BorrowRecord ||--|| Device : involves
    BorrowRecord ||--|| User : involves
    ApprovalRecord ||--|| User : involves
    Notification ||--|| User : involves

    User {
        int user_id PK "用户唯一标识"
        varchar username "用户名"
        varchar pswd_hash "加密后的密码哈希值"
        int user_type "用户类型"
        varchar name "用户姓名"
        int gender "性别"
        varchar dpt "所属院系或专业"
        varchar title "职称"
        int status "用户状态"
    }

    Device {
        int device_id PK "设备唯一标识"
        varchar device_name "设备名称"
        varchar model "设备型号"
        date purchase_date "购入时间"
        decimal price "设备价格"
        int status "设备状态"
        varchar lab "所属实验室"
        int can_borrow "是否可以借用"
    }

    BorrowRecord {
        int record_id PK "借还记录唯一标识"
        int user_id FK "借用人ID"
        int device_id FK "借用设备ID"
        date borrow_date "借用日期"
        date return_date "归还日期"
        int approval_status "审批状态"
    }

    ApprovalRecord {
        int approval_id PK "审批记录唯一标识"
        int record_id FK "借还记录ID"
        int approver_id FK "审批人ID"
        date approval_date "审批日期"
        text approval_comment "审批意见"
    }

    Notification {
        int notification_id PK "通知唯一标识"
        int user_id FK "接收通知的用户ID"
        int type "通知类型"
        text content "通知内容"
        int related_id "相关记录ID"
        timestamp created_at "通知创建时间"
        int read_status "阅读状态"
    }

    Log {
        int log_id PK "日志记录唯一标识"
        int user_id FK "操作用户ID"
        int action "操作类型"
        text details "操作详情"
        timestamp timestamp "操作发生的时间"
    }

    DeviceType {
        int type_id PK "类型唯一标识"
        varchar type_name "设备类型名称"
        varchar model "设备型号"
        text description "设备描述"
    }
```



## 网页设计

```mermaid
graph TD
登录页-->注册页
注册页-->主页
登录页-->主页
主页-->借用申请
主页-->归还
主页-->通知中心
主页-->查询与编辑*
主页-->审批*

```



| **中文名**           | **英文名**      | **完成状态** |
| -------------------- | --------------- | ------------ |
| 登录页               | `login`         | ✔️            |
| 注册页               | `sign_up`       | ✔️            |
| 主页                 | `index`         | ✔️            |
| 申请借用             | `borrow`        | ✔️            |
| 归还                 | `return`        | ✔️            |
| 通知中心             | `notifications` | ✔️            |
| 查询与编辑（管理员） | `edit_devices`  | ✔️            |
| 审批（管理员）       | `review`        | ✔️            |

### 变动一

不再单独提供查询页面

可以注意到：

- 借用本质上是**先查询可用设备**，再借用
- 归还本质上是**先查询已借设备**，再归还
- 编辑设备信息和删除设备本质上是**先查询全部设备**，再操作

因此，**按条件查询是一个已经包含在大多数过程里的过程**，需要多次复用，无需独立存在。并且用户事实上不用关心全部的实验设备的信息，只需要关心如何对所预期的设备进行操作

### 变动二

新增设备最终纳入编辑设备，虽然新增设备不需要查询，但逻辑上与编辑已有设备的信息和删除已有设备是同一类操作

### 变动三

借用和归还现已拆分为两个页面。在变动一里提到过，两者需要查询的范围是不同的。先前合并两者并且与查询独立放置的举动是没有道理的



## 部署运行

### 一、配置 Python 虚拟环境

推荐使用虚拟环境进行部署：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
.\\venv\scripts\activate  # Windows PowerShell

# 更新pip并安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt
```

当前开发环境是 Windows 11 23H2 下的 Python 3.9，如果在其他环境中部署出现错误，请提 issue 或者咨询 AI。



### 二、配置 MySQL 数据库

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS equipment_mgr;
USE equipment_mgr;

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
    return_deadline DATE,
    approval_status INT NOT NULL,
    approver_id INT,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (device_id) REFERENCES devices(device_id),
    FOREIGN KEY (approver_id) REFERENCES users(user_id)
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

-- 创建 notifications 表
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type INT NOT NULL,
    content TEXT NOT NULL,
    related_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_status INT NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

```

添加用户：

```sql
CREATE USER 'equipment_mgr'@'localhost' IDENTIFIED BY 'your_password_here';
GRANT ALL PRIVILEGES ON equipment_mgr.* TO 'equipment_mgr'@'localhost';
FLUSH PRIVILEGES;
```



### 三、运行

```bash
python app.py
```

