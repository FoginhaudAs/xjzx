from redis import StrictRedis
import logging


class BaseConfig(object):
    """配置基类"""

    # mysql数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:6379/information'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis数据库配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 设置session加密字符串
    SESSION_KEY = 'ADFKJLIEAFJEIOADJ'

    # 设置session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=1)
    SESSION_USE_SIGNET = True
    SESSION_PERMENT = False
    PERMENT_SESSION_LIFETIME = 86400


class DevelopmentConfig(BaseConfig):
    """开发者配置类"""
    DEBUG = True
    LOG_LEVER = logging.DEBUG

class ProductConfig(BaseConfig):
    """线上配置类"""
    DEBUG = False
    LOG_LEVER = logging.ERROR


Config_dict = {'development':DevelopmentConfig, 'production':ProductConfig}