# -*- coding: utf-8 -*-

import time
import json
import random
import hashlib
import requests

headerdata = {"Content-type": "application/json"}

#get depth(orders)
body = {"method": "depth.query", "params": ["TOP/ETH", 10], "id": 0}
res = requests.post(
    "https://depth.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

appid = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
appkey = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'

#get token
num = random.randint(100000, 999999)
curtime = int(time.time())
data = 'appkey=' + appkey + '&random=' + str(num) + '&time=' + str(curtime)
sha256 = hashlib.sha256()
sha256.update(data.encode('utf-8'))
signature = sha256.hexdigest()
params = {
    'appid': appid,
    'time': str(curtime),
    'random': num,
    'sig': signature
}
res = requests.get("https://server.top.one/api/apiToken", params=params)
print(res.text)

token = json.loads(res.text)['data']['apitoken']

#balance
# 1)查询余额
body = {"method": "balance.query", "params": [token], "id": 0}
res = requests.post(
    "https://trade.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

#current orders
# 2)当前委托
body = {"method": "order.query", "params": [token, 0, 100], "id": 0}
res = requests.post(
    "https://trade.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

#put limit order
# 3)限价单
body = {
    "method": "order.limit",
    "params": [token, "TOP/ETH", 2, "100", "0.0001", 0],
    "id": 0
}  #买入 100TOP， 价格0.0001
res = requests.post(
    "https://trade.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

#put market order
# 4)市价单
body = {
    "method": "order.market",
    "params": [token, "TOP/ETH", 2, "0.1", 0],
    "id": 0
}  #买入，0.1ETH
res = requests.post(
    "https://trade.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

#cancel order
# 5)撤单
order_id = 101  #your order id , need change!
body = {
    "method": "order.cancel",
    "params": [token, "TOP/ETH", order_id],
    "id": 0
}
res = requests.post(
    "https://trade.top.one/", data=json.dumps(body), headers=headerdata)
print(res.text)

#history orders
# 6)历史委托
body = {
    "method": "order.history",
    "params": [token, "TOP/ETH", 0, 0, 0, 100],
    "id": 0
}
res = requests.post(
    "https://trade.top.one/history/",
    data=json.dumps(body),
    headers=headerdata)
print(res.text)
