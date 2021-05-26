from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
# Session拓展工具：将session中的存储调整到redis数据库中去
from flask_session import Session
from config import Config_dict
from .views import *
from logging.handlers import RotatingFileHandler
import logging


db = SQLAlchemy()

reids_obj = None

# 添加日志
def write_log(log_level):
    # 设置日志的记录等级
    logging.basicConfig(level=log_level)
    # 创建日志记录器
    file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式  日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

def create_app(config_type='production'):

    ConfigType = Config_dict[config_type]
    write_log(ConfigType.LOG_LEVER)
    app = Flask(__name__)
    app.config.from_object(ConfigType)
    db.init_app(app)
    global redis_obj
    redis_obj = StrictRedis(host=ConfigType.REDIS_HOST, port=ConfigType.REDIS_PORT, decode_responses=True)
    CSRFProtect(app)
    Session(app)

    return app