from os import abort
from info import redis_obj
from info.constants import IMAGE_CODE_REDIS_EXPIRES
from . import passport_bp
from flask import request, make_response
from info.utils.captcha.captcha import captcha


# 修饰视图函数
@passport_bp.route('/image_code')
def get_image_code():
    """获取图片验证码"""
    # 1.获取参数
    code_id = request.args.get('code_id')
    # 2.校验参数
    if not code_id:
        return abort(404)
    # 3.业务逻辑
    # 3.1获取图片验证码参数（图片名称 图片真实值 图片二进制数据）
    image_name, image_real_code, image_data = captcha.generate_captcha()
    # 3.2以code_id为key将图片真实值保存到redis数据库
    redis_obj.setex('imageCode_%s' % code_id, IMAGE_CODE_REDIS_EXPIRES, image_data)
    # 4.返回值（图片二进制数据）
    response = make_response(image_data)
    response.headers['Content-Type'] = 'png/image'
    return response

