from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
import pymysql
from flask_wtf.csrf import CSRFProtect
# Session拓展工具：将session中的存储调整到redis数据库中去
from flask_session import Session
# 存储数据用到的session
from flask import session
pymysql.install_as_MySQLdb()


class Config(object):
    DEBUG = True
    # mysql数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:123456@127.0.0.1:6379/flask_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # 配置redis数据库
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

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)
CSRFProtect(app)
Session(app)


@app.route('/')
def func():
    session['name'] = 'laowang'
    return 'hello world'


if __name__ == '__main__':
    app.run(debug=True)