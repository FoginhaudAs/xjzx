from flask import current_app, session, render_template
from info.modules.index import index_bp
from info.models import User


# 装饰视图函数
@index_bp.route('/')
def index():
    current_app.logger.debug('This is a debug log')
    session['name'] = 'laowang'
    return render_template('news/index.html')

@index_bp.route('/favicon.ico')
def get_favicon_ico():
    """返回网站的图标"""
    return current_app.send_static_file('news/favicon.ico')