from flask import Blueprint, session, current_app
import logging

# 创建蓝图对象
index_bp = Blueprint('index_bp', __name__)

# 装饰视图函数
@index_bp.route('/')
def index():
    logging.debug("This is a debug log.")

    current_app.logger.debug('This is a debug log')
    session['name'] = 'laowang'
    return 'hello world'