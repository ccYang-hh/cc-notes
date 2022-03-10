import requests
from lxml import etree
from tools.utils import create_headers, get_proxy_ip
from django.utils.http import urlquote
import re


headers = create_headers()
proxies = {
    'http': get_proxy_ip()
}
key = input('请输入：')
url = f'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
# response = requests.get(url=url, headers=headers, proxies=proxies)
dats = {
    "i": key,
    "from": "AUTO",
    "to": "AUTO",
    "smartresult": "dict",
    "client": "fanyideskweb",
    "salt": "16460387271865",
    "sign": "0601e9ace2edd9e84239f1afbf4aef45",
    "lts": "1646038727186",
    "bv": "56d33e2aec4ec073ebedbf996d0cba4f",
    "doctype": "json",
    "version": "2.1",
    "keyfrom": "fanyi.web",
    "action": "FY_BY_REALTlME",
}
# data = {
#     "from": "zh",
#     "to": "en",
#     "query": key,
#     # "transtype": "realtime",
#     # "simple_means_flag": 3,
#     # "sign": "752449.1022064",
#     # "token": "001d535521af9e2763c8871e3118d2e4",
#     # "domain": "common"
# }
response = requests.post(url=url, data=dats, headers=headers, proxies=proxies)
print(response.json())
# tree = etree.HTML(response.json())
#
# content = tree.xpath("//div[@class='content']//div[@class='lemma-summary']//text()")
# print(''.join(content[1:-1]).replace(r'\[\w+\s+\d+\]',''))
