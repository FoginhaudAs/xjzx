from flask import current_app, session, render_template, jsonify

from info import db
from info.modules.index import index_bp
from info.models import User


# 装饰视图函数
from info.response_code import RET


@index_bp.route('/')
def index():
    """访问首页接口"""

    # 1.查询当前用户信息
    user_id = session.get('user_id')
    user = None # type:User
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    # 2.将用户信息转化成字典
    user_dict = user.to_dict() if user else None
    # 3.将用户信息传至前端
    data = {
        'user_info':user_dict
    }

    return render_template('news/index.html', data = data)

@index_bp.route('/favicon.ico')
def get_favicon_ico():
    """返回网站的图标"""
    return current_app.send_static_file('news/favicon.ico')