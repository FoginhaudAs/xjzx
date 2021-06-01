from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
# Session拓展工具：将session中的存储调整到redis数据库中去
from flask_session import Session
from config import Config_dict
from logging.handlers import RotatingFileHandler
import logging


db = SQLAlchemy()

redis_obj = None  # tpye: StrictRedis

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
    """创建app"""
    # 设置配置类
    ConfigType = Config_dict[config_type]
    # 创建日志
    write_log(ConfigType.LOG_LEVER)
    # 生成app对象
    app = Flask(__name__)
    # app项目引用配置类
    app.config.from_object(ConfigType)
    # 项目关联数据库
    db.init_app(app)
    # 获取redis数据库对象
    global redis_obj
    redis_obj = StrictRedis(host=ConfigType.REDIS_HOST, port=ConfigType.REDIS_PORT, decode_responses=True)
    # 注册蓝图对象
    from info.modules.index import index_bp
    app.register_blueprint(index_bp)
    # 注册另一个蓝图对象
    from info.modules.passport import passport_bp
    app.register_blueprint(passport_bp)
    # 开启CSRF保护机制
    CSRFProtect(app)
    # 将session内容存储到redis数据库
    Session(app)
    # 返回app对象
    return app