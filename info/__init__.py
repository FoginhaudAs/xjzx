from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
# Session拓展工具：将session中的存储调整到redis数据库中去
from flask_session import Session
from config import Config_dict
from .views import *


db = SQLAlchemy()

reids_obj = None

def create_app(config_type='production'):

    ConfigType = Config_dict[config_type]
    app = Flask(__name__)
    app.config.from_object(ConfigType)
    db.init_app(app)
    global redis_obj
    redis_obj = StrictRedis(host=ConfigType.REDIS_HOST, port=ConfigType.REDIS_PORT, decode_responses=True)
    CSRFProtect(app)
    Session(app)

    return app