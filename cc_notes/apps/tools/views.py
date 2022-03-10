from django.utils.http import urlquote
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes, throttle_classes
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from random import randint
import requests
from lxml import etree
import re
from django_redis import get_redis_connection
from django.utils.http import urlquote
import asyncio
import aiohttp
from functools import wraps
from asyncio.proactor_events import _ProactorBasePipeTransport

from users.models import User
from notes.models import Article
from feeds.models import Feed
from .utils import send_mail, get_ip, create_headers, get_proxy_ip

# Create your views here.


@api_view(['POST'])
def set_verify_code(request):
    # 发送邮箱验证码，并存储在redis服务器中
    mode = request.data['mode']
    value = request.data['value']
    redis_conn = get_redis_connection('verify_codes')
    code = '%06d' % randint(0, 999999)

    if mode == 'email':
        redis_conn.setex('mail_%s' % value, 600, code)
        send_mail(value, code)
    elif mode == 'mobile':
        redis_conn.setex('mobile_%s' % value, 600, code)
    context = {
        'value': value,
        'code': code
    }
    return Response(context)


@api_view(['POST'])
def check_code(request):
    # 测试验证码是否正确
    mode = request.data['mode']
    value = request.data['value']
    browser_code = request.data['code']
    redis_conn = get_redis_connection('verify_codes')
    if mode == 'email':
        code = redis_conn.get('mail_%s' % value)
    elif mode == 'mobile':
        code = redis_conn.get('mobile_%s' % value)
    if code is None:
        return Response({
            'message': '验证码已过期或该账户尚未注册！',
            'status': 0
        })
    elif bytes.decode(code) != str(browser_code):
        return Response({
            'message': '验证码错误，请检查填写是否正确！',
            'status': 0
        })
    else:
        return Response({
            'status': 1
        })


@api_view(['GET'])
def get_user_location(request):
    ip = get_ip(request)
    # print(request.META.get('REMOTE_ADDR'))
    # print(request)
    ak = "rHpPbxqyFw0VqoDOc9ot8cZA8up7xwyT"
    # https://api.map.baidu.com/location/ip?ak=rHpPbxqyFw0VqoDOc9ot8cZA8up7xwyT&coor=bd09ll
    url = f"https://api.map.baidu.com/location/ip?ak={ak}&coor=bd09ll"
    headers = {
        "USER_AGENT":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    location = requests.get(url=url, headers=headers).json()
    return Response(location)


class WeatherAnonThrottle(AnonRateThrottle):
    rate = '30/day'


class WeatherUserThrottle(UserRateThrottle):
    rate = '30/day'


@api_view(['GET'])
@throttle_classes([WeatherAnonThrottle, WeatherUserThrottle])
def get_weather(request):
    ak = "76b37bafa688f1d89ad44ee0b7c4744e"
    city = urlquote('开封')
    url = f"http://apis.juhe.cn/simpleWeather/query?city={city}&key={ak}"
    headers = {
        "USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    }
    weather_info = requests.get(url=url, headers=headers).json()
    return Response(weather_info)


# 定义一个协程函数用于爬取关键字信息
async def fetch_bk(url, headers, proxy):
    # 生成etree
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers, proxy=proxy) as response:
            # text()返回字符串类型的响应数据
            # read()获得二进制形式响应数据
            # json()获得json形式响应数据
            page_text = await response.text()
            tree = etree.HTML(page_text)
            content = tree.xpath("//div[@class='content']//div[@class='lemma-summary']//text()")
            if content:
                summary = re.sub(r'\[[\d-]+\]', '', ''.join(content[1:-1]))
                result = re.sub(r'\s+', '', summary)
                return result
            else:
                return None


# 协程任务池批量爬取
# async def main_fetch_bk(url, total, headers, proxy):
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for i in range(total):
#             new_url = f'{url}pg{i + 1}'
#             tasks.append(asyncio.create_task(fetch_bk(session, new_url, headers, proxy)))
#         done, pending = await asyncio.wait(tasks)
#         return done


# 解决RuntimeError: Event loop is closed问题
# aiohttp 内部使用了 _ProactorBasePipeTransport ，程序退出释放内存时自动调用其 __del__ 方法导致二次关闭事件循环
def silence_event_loop_closed(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except RuntimeError as e:
            if str(e) != 'Event loop is closed':
                raise
    return wrapper


_ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)


@api_view(['GET'])
def get_bk_results(request, keyword):
    headers = create_headers()
    proxy = get_proxy_ip()
    target_url = f'https://baike.baidu.com/item/{urlquote(keyword)}'
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(fetch_bk(url=target_url, headers=headers, proxy=proxy))
    done = asyncio.run(fetch_bk(url=target_url, headers=headers, proxy=proxy))
    return Response({
        "code": 200,
        "result": done
    })

