from flask import Blueprint


# 创建蓝图对象
passport_bp = Blueprint('passport', __name__, url_prefix='/passport')

# 导入文件中的视图函数
from .views import *