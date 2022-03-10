from django.contrib.auth.backends import ModelBackend
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
import re, datetime
import jwt

from .models import User

UserModel = get_user_model()


def get_user_by_account(account):
    """
    通过account获取用户
    account：username or mobile
    以这种方式获取用户需要注意用户名与手机号和邮箱可能混淆的问题
    """
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        elif re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[com,cn,net]{1,3}$', account):
            user = User.objects.get(email=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class WithMobileModelBackend(ModelBackend):
    """
    重写django的ModelBackend的authenticate方法以实现对手机号和邮箱的验证登陆
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        # 获取用户
        user = get_user_by_account(username)
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user


# 将时间戳转换为标准日期格式
def time_converter(timestamp):
    dateArray = datetime.datetime.utcfromtimestamp(timestamp) + datetime.timedelta(hours=8)
    formatTime = dateArray.strftime("%Y-%m-%d %H:%M:%S")
    return str(formatTime)



# from rest_framework_jwt.settings import api_settings
# from rest_framework_jwt.utils import jwt_get_secret_key
# 重写jwt响应，未使用
# def jwt_response_payload_handler(token, user=None, request=None):
#     """
#     重写jwt的响应方法以返回除token以外的更多数据（用户名、用户id）
#     """
#     # user = authenticate(username=user.username, password=user.password)
#     # user = get_object_or_404(User, id=user.id)
#     # if user is None:
#     #     return Response({'message': '用户不存在！'}, status=status.HTTP_404_NOT_FOUND)
#     # else:
#     #     login(request, user)
#     #     print(request.user)
#     return {
#         'token': token,
#         'username': user.username,
#         'user_id': user.id
#     }

# jwt自定义函数，未使用
# def jwt_encode_handler(payload):
#     key = api_settings.JWT_PRIVATE_KEY or jwt_get_secret_key(payload)
#     target = jwt.encode(
#         payload,
#         key,
#         api_settings.JWT_ALGORITHM
#     ).decode()
#     print(target, type(target))
#     return target
