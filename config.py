import os

class Config:
    SECRET_KEY = 'dev-key-12345'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'           # MySQL的root用户
    MYSQL_PASSWORD = '123456'       # 你的MySQL root密码，请修改为你的实际密码
    MYSQL_DB = 'equipment_mgr'
    MYSQL_PORT = 3306