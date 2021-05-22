from flask import Blueprint, session


# 创建蓝图对象
index_bp = Blueprint('index_bp', __name__)

# 装饰视图函数
@index_bp.route('/')
def func():
    session['name'] = 'laowang'
    return 'hello world'