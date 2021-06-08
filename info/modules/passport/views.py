import random
from datetime import datetime
from os import abort
from info import redis_obj, db
from info.constants import *
from info.lib.yuntongxun.sms import CCP
from info.models import User
from info.response_code import RET
from . import passport_bp
from flask import request, make_response, jsonify, current_app, session
from info.utils.captcha.captcha import captcha
import re


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
    redis_obj.setex('imageCode_%s' % code_id, IMAGE_CODE_REDIS_EXPIRES, image_real_code)
    # 4.返回值（图片二进制数据）
    response = make_response(image_data)
    response.headers['Content-Type'] = 'png/image'
    return response


@passport_bp.route('/sms_code', methods=['POST'])
def send_sms_code():
    """发送短信验证码接口"""

    # 1.获取参数
    # 1.1 mobile: 手机号码， image_code:用户填写的图片验证码值， image_code_id: UUID编号
    param_dict = request.json
    mobile = param_dict.get('mobile')
    image_code = param_dict.get('image_code')
    image_code_id = param_dict.get('image_code_id')
    # 2.校验参数
    # 2.1 非空判断
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')
    # 2.2 手机号码格式校验
    if not re.match(r'1[35678][0-9]{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码有误')

    # 3.逻辑处理
    # 3.1 根据image_code_id编号去redis中获取正确真实的图片验证码值
    try:
        real_image_code = redis_obj.get('imageCode_%s' % image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询图片验证码真实值错误')

    if real_image_code:
        # 3.1.1 真实的图片验证码有值：将值从redis数据库删除 [避免拿着这个值多次判断]
        redis_obj.delete(real_image_code)
    else:
        # 3.1.2 真实的图片验证码没有值：图片验证码值过期了
        return jsonify(errno=RET.NODATA, errmsg='图片验证码已过期')
    # 3.2 比对用户填写的图片验证码值 & 正确的图片验证码真实值
    if real_image_code.lower() != image_code.lower():
        # 3.3 不相等：返回错误状态码，提示图片验证码填写错误
        return jsonify(errno=RET.DATAERR, errmsg='验证码填写错误')
    # TODO: 提前判断手机号码是否注册过，数据库查询 [提高用户体验]

    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='用户注册信息查询错误')
    if user:
        return jsonify(errno=RET.DATAEXIST, errmsg='手机号码已注册')
    # 3.4 发送短信验证码
    # 3.4.1 生成6位的随机短信验证码值
    real_sms_code = '%06d' % random.randint(0, 999999)
    # 3.4.2 调用CCP类发送短信验证码
    try:
        result = CCP().send_template_sms('18344015034', [real_sms_code, SMS_CODE_REDIS_EXPIRES/60], 1)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='短信验证码发送失败')

    if result == -1:
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')
    # 3.4.3 发送短信验证码成功后，保存6位的短信验证码值到redis数据库
    redis_obj.setex('SMS_%s' % mobile, SMS_CODE_REDIS_EXPIRES, real_sms_code)
    # 4.返回值
    # 4.1 发送短信验证码成功
    return jsonify(errno=RET.OK, errmsg='短信验证码发送成功')

@passport_bp.route('/register', methods=['POST'])
def regitster():
    """注册后端接口"""
    # 1.获取参数
    # 1.1 mobile: 手机号码， sms_code:用户填写的短信验证码， password:未加密的密码
    parmar_dict = request.json
    mobile = parmar_dict.get('mobile')
    sms_code = parmar_dict.get('sms_code')
    password = parmar_dict.get('password')
    # 2.参数校验
    # 2.1 非空判断
    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')
    # 2.2 手机号码格式判断
    if not re.match(r'1[35678][0-9]{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码有误')
    # 3.逻辑处理
    # 3.1 根据手机号码作为key去redis数据库获取真实的短信验证码值
    try:
        real_sms_code = redis_obj.get('SMS_%s' % mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    if real_sms_code:
        # 有值：将真实的短信验证码值从redis数据库删除
        redis_obj.delete(mobile)
    else:
        # 没有值：短信验证码过期了
        return jsonify(errno=RET.NODATA, errmsg='短信验证码过期')
    # 3.2 对比用户填写的短信验证码值和真实的短信验证码值是否一致
    if sms_code != real_sms_code:
        return jsonify(errno=RET.PARAMERR, errmsg='短信验证码错误')
    # 相等：注册
    # 不相等：填写的短信验证码错误
    # 3.3 注册：创建用户对象，并给各个属性赋值
    user = User()
    user.nick_name = mobile
    user.mobile = mobile
    # TODO: 密码加密
    user.password = password
    user.last_login = datetime.now()
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    # 3.4 注册成功一般要求登录成功，使用session记录用户登录信息
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['user_id'] = user.id
    # 4.返回值
    # 4.1 返回注册成功
    return jsonify(errno=RET.OK, errmsg='注册成功')

@passport_bp.route('/login', methods=['POST'])
def login():
    """登录后端接口"""
    # 1.获取参数
    # 1.1 mobile:用户输入的手机号码 password:用户输入的密码
    param_dict = request.json
    mobile = param_dict.get('mobile')
    password = param_dict.get('password')
    # 2.校验参数
    # 2.1 非空校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不足')
    # 2.2 手机号码格式校验
    if not re.match(r'1[35678][0-9]{9}', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码有误')
    # 3.业务逻辑
    # 3.1根据mobile去数据库查询用户
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='数据库查询错误')
    if not user:
        # 没有值：用户不存在
        return jsonify(errno=RET.USERERR, errmsg='用户不存在')
    # 3.2比较用户输入的密码与数据库获取的用户未加密的密码是否一致
    if not user.check_password(password):
        # 不一致：用户名或密码错误
        return jsonify(errno=RET.PWDERR, errmsg='用户名或密码错误')
    # 一致：登录成功，更新last_login和登录状态
    user.last_login = datetime.now()
    # 将用户修改操作提交到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='数据库保存信息错误')
    # 3.3 保存用户数据
    session['nick_name'] = user.nick_name
    session['mobile'] = user.mobile
    session['user_id'] = user.id
    # 4.返回值
    # 登录成功
    return jsonify(errno=RET.OK, errmsg='登录成功')
