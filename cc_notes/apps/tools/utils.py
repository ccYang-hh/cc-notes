from cc_notes.configs import dev
import requests
from fake_useragent import UserAgent
from rest_framework.response import Response


def send_mail(email, code):

    from django.core.mail import EmailMultiAlternatives

    subject = '来自<CC笔记>的注册确认邮件'

    content = f'嗨！感谢注册CC笔记在线写作平台，衷心的感谢您！祝您事事顺心，心想事成，吉祥安康！这里是注册用的验证码：{code}。注意！该验证码有效期只有10分钟！请尽快注册！'

    html_content = '''
                        <p>嗨！感谢注册CC笔记，衷心的感谢您！祝您事事顺心，心想事成，吉祥安康！</p>
                        <p>这里是注册用的验证码：{}</p>
                        <p>注意！该验证码有效期只有10分钟！请尽快注册！</p>
                    '''.format(code)

    msg = EmailMultiAlternatives(subject, content, dev.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def get_ip(request):
    """
    获取请求者的IP信息
    X-Forwarded-For:简称XFF头，它代表客户端，也就是HTTP的请求端真实的IP，只有在通过了HTTP代理或者负载均衡服务器时才会添加该项
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')  # 判断是否使用代理
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 使用代理获取真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 未使用代理获取IP
    return ip


ua = UserAgent(use_cache_server=False)


def create_headers(referer=None):
    headers = dict()
    headers["User-Agent"] = ua.random
    if referer:
        headers["Referer"] = referer
    return headers


def get_proxies(num=1, api_type=2, mr=1 ):
    proxies = []
    try:
        url = f'http://tiqu.pyhttp.taolop.com/getip?count={num}&neek=21168&type={api_type}&yys=0&port=1&sb=&mr={mr}&sep=1&time=2'
        response = requests.get(url=url, headers=create_headers()).json()
        if response["success"] == "true":
            for proxy_ip in response["data"]:
                proxies.append(proxy_ip["ip"])
    except Exception as e:
        raise Exception("获取代理异常")


def get_proxy_ip(api_type=2, mr=1, port=1):
    """
    获取代理ip
    :param num: 获取数量
    :param api_type: 代理ip返回内容格式（ 1：返回txt，2：返回json，3：返回html）
    :param mr: 代理ip是否去重（1：360天去重，2：24小时去重，3：不去重）
    :param port: 代理协议（1：http，2：https，11：socket5）
    """
    try:
        url = f'http://tiqu.pyhttp.taolop.com/getip?count=1&neek=21168&type={api_type}&yys=0&port={port}&sb=&mr={mr}&sep=0&ts=1&time=2'
        response = requests.get(url=url, headers=create_headers()).json()
        if response["success"]:
            proxy_item = response["data"][0]
            proxy_ip = proxy_item["ip"]
            proxy_port = proxy_item["port"]
            if port == 1:
                return f"http://{proxy_ip}:{proxy_port}"
            else:
                return f"https://{proxy_ip}:{proxy_port}"
    except Exception as e:
        raise Response({"message": "获取代理异常"})