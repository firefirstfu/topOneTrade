"""
市場行情查詢模組
"""

import time
import datetime
import os, sys
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pprint
pp = pprint.PrettyPrinter(width=41, compact=True)

import requests

import config as CONFIG
from apiToken import API

HEADER_DATA = {"Content-type": "application/json"}

# 貨幣市場深度
depthNum = CONFIG.DEPTH_NUM


class Quotation(object):
    """
    市場行情查詢
    """

    @classmethod
    def depth(cls, tradePair: str) -> tuple:
        """
        查詢市場深度
        @ bids: 委買價
        @ asks: 委賣價
        """
        try:
            body = {
                "method": "depth.query",
                "params": [tradePair, depthNum],
                "id": 0
            }
            res = requests.post(
                CONFIG.MARKET_DEPTH_URL,
                data=json.dumps(body),
                headers=HEADER_DATA,
            ).text
            res = json.loads(res)
            # 委買價
            bids = res['result'][0]['bids']
            # 委賣價
            asks = res['result'][0]['asks']

        except Exception as e:
            print(e)
            bids, asks = None

        return bids, asks

    @classmethod
    def getBest1stGear(cls, tradePair: str) -> dict:
        """
        取得最佳1檔
        """
        # 最佳5檔
        bids, asks = cls.depth(tradePair)

        try:
            # 最高委買價
            highBuyPrice = float(bids[0][0])
            # 最高委買量
            hightBuyVol = float(bids[0][1])
            # 最低委賣價
            lowSellPrice = float(asks[0][0])
            # 最低委賣價
            lowSellVol = float(asks[0][1])
            rs = {
                'buy': {
                    'highBuyPrice': highBuyPrice,
                    'hightBuyVol': hightBuyVol,
                },
                'sell': {
                    'lowSellPrice': lowSellPrice,
                    'lowSellVol': lowSellVol,
                },
            }
        except Exception as e:
            print(e)
            rs = None

        # pp.pprint(rs)
        return rs

    @classmethod
    def getHistoryDeals(cls):
        """
        取得歷史成交(計算當日交易量)
        """

        # print('取得歷史成交')
        token = API.getToken()

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        yesterday_end_time = int(
            time.mktime(time.strptime(str(today), '%Y-%m-%d'))) - 1
        # 今天開始unintime
        today_start_time = yesterday_end_time + 1
        # 今天结束时间戳
        today_end_time = int(
            time.mktime(time.strptime(str(tomorrow), '%Y-%m-%d'))) - 1
        # print(today_start_time)
        # print(today_end_time)

        rangLt = []
        # reqLst = [0, 101, 201, 301, 401, 501]
        reqLst = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        for r in reqLst:
            body = {
                "method":
                "order.history",
                "params":
                [token, 'LVE/ETH', today_start_time, today_end_time, r, 100],
                "id":
                0
            }
            res = requests.post(
                CONFIG.HISTORY_DEALS,
                data=json.dumps(body),
                headers=HEADER_DATA)
            res = json.loads(res.text)
            # pp.pprint(res)
            records = res['result']['records']
            if len(records) != 0:
                rangLt.extend(records)

        amounts = 0
        for item in rangLt:
            amounts += float(item['amount'])
        # pp.pprint(len(rangLt))
        # pp.pprint(rangLt)
        # pp.pprint(amounts)
        return amounts


if __name__ == "__main__":
    # 最佳5檔
    # bids, asks = Quotation.depth('LVE/ETH')
    # pp.pprint(bids)
    # pp.pprint(asks)

    # 最佳1檔
    # rs = Quotation.getBest1stGear('LVE/ETH')

    # 取得歷史成交交易量
    rs = Quotation.getHistoryDeals()
    print(f'今日總成交量: {rs}')
