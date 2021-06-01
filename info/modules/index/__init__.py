from flask import Blueprint


# 创建蓝图对象
index_bp = Blueprint('index_bp', __name__)

from .views import *