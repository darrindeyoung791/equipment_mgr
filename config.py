from os import environ, path
from dotenv import load_dotenv

# 加载环境变量
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    # Flask配置
    SECRET_KEY = environ.get('SECRET_KEY') or 'dev'
    
    # MySQL配置
    MYSQL_HOST = environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = environ.get('MYSQL_DB') or 'equipment_mgr'
    MYSQL_CURSORCLASS = 'DictCursor'
    
    # 应用配置
    DEBUG = environ.get('FLASK_DEBUG') or True
