from rest_framework.views import exception_handler as drf_exception_handler
import logging
from django.db import DatabaseError
from redis.exceptions import RedisError
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

# 获取在配置文件中定义的名叫django的日志器
logger = logging.getLogger('django')


def exception_handler(exc, context):
    """
    自定义异常处理：drf框架的exception_handler会对404异常、PermissionDenied异常以及APIException
    异常进行处理，该函数的目的是处理一些其他的异常并将之存储在日志中，比如数据库异常以及redis异常
    参数说明：
        exc : 异常
        context : 抛出异常的上下文，包含request和view对象
    返回值 : response响应
    """

    # 调用drf框架原生的异常处理方法
    response = drf_exception_handler(exc, context)

    # 添加状态码的错误显示
    if response is not None:
        response.data['status_code'] = response.status_code

    if response is None:
        view = context['view']
        if isinstance(exc, DatabaseError):
            logger.error("[%s] %s" % (view, exc))
            response = Response({'message': 'mysql数据库错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
        if isinstance(exc, RedisError):
            logger.error("[%s] %s" % (view, exc))
            response = Response({'message': 'redis数据库错误'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)
    return response


