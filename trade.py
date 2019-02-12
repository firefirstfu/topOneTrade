"""
交易模組
"""

import json
import time
import pprint
pp = pprint.PrettyPrinter(width=41, compact=True)
from multiprocessing import Pool

import requests

import config as CONFIG
from apiToken import API
from market import Quotation

HEADER_DATA = {"Content-type": "application/json"}

# 請求帳戶貨幣餘額種類
BALANCE_TOKENS = ('LVE', 'ETH', 'TOP')
# 刷量次數
BRUSH_NUM = CONFIG.BRUSH_NUM
# 每次下單間隔休眠時間
TRADE_SLEEP_TIME = CONFIG.TRADE_SLEEP_TIME
# 刷量每次單次token數量
BRUSH_TOKEN_NUM = CONFIG.BRUSH_TOKEN_NUM
# 操盤手Bot委買價
ORDER_BUY_PRICE = CONFIG.ORDER_BUY_PRICE
# 操盤手Bot委賣價
ORDER_SELL_PRICE = CONFIG.ORDER_SELL_PRICE


class MoneyManage(object):
    """
    資金控管
    """

    @classmethod
    def balance(cls, tokens: tuple = None):
        """
        帳戶貨幣餘額
        {'total': '1.1075', 'asset': 'ETH', 'lock': '0', 'full_name': 'Ethereum', 'btcvalue': '0', 'freeze': '0', 'available': '1.1075', 'ethvalue': '1.1075'}
        """

        token = API.getToken()
        body = {"method": "balance.query", "params": [token], "id": 0}
        res = requests.post(
            CONFIG.TRADE_URL,
            data=json.dumps(body),
            headers=HEADER_DATA,
        )
        res = json.loads(res.text)
        accountLst = res['result']

        balanceDic = {}
        if tokens is not None:
            # 部份取得
            for t in tokens:
                for item in accountLst:
                    if t in item.values():
                        balanceDic[t] = item
                        break
        else:
            # 全部取得
            tokens = []
            for a in accountLst:
                tokens.append(a['asset'])

            for t in tokens:
                for item in accountLst:
                    if t in item.values():
                        balanceDic[t] = item
                        break

        # pp.pprint(accountLst)
        return balanceDic

    @classmethod
    def isEnough(cls, tradePair: str, tradeType: str, tokenAmt: float) -> bool:
        """
        帳戶Token/金額是否足夠
        : param tradePair:  貨幣兌
        : param tradeType:  交易類型(buy/sell)
        : param tokenAmt:   交易數量
        """

        mainToken, viceToken = tradePair.split('/')

        # 帳戶餘額
        balances = cls.balance(BALANCE_TOKENS)

        # 市場最佳1檔價格
        bestPrice = Quotation.getBest1stGear(tradePair)
        # 委買最高價
        hightBuyPrice = float(bestPrice['buy']['highBuyPrice'])
        # 委賣最低價
        lowSellPrice = float(bestPrice['sell']['lowSellPrice'])

        # 買進LVE
        if tradeType == 'buy':

            # buy token購買總額
            buyAmts = lowSellPrice * tokenAmt
            # sell token餘額
            sellAmts = float(balances[viceToken]['available'])

            # 計算是否足夠
            if sellAmts >= buyAmts:
                return (True, {
                    'hightBuyPrice': hightBuyPrice,
                    'lowSellPrice': lowSellPrice,
                    'tokenAmt': tokenAmt,
                    'bestPrice': bestPrice,
                    'balances': balances
                }, '足夠')
            else:
                return (False, {
                    'hightBuyPrice': hightBuyPrice,
                    'lowSellPrice': lowSellPrice,
                    'tokenAmt': tokenAmt,
                    'bestPrice': bestPrice,
                    'balances': balances
                }, '不足夠')

        # 賣出LVE
        if tradeType == 'sell':

            # buy token購買總額
            balanceToken = float(balances[mainToken]['available'])
            # sell token餘額
            sellAmts = tokenAmt

            # 計算是否足夠
            if balanceToken >= sellAmts:
                return (True, {
                    'hightBuyPrice': hightBuyPrice,
                    'lowSellPrice': lowSellPrice,
                    'tokenAmt': tokenAmt,
                    'bestPrice': bestPrice,
                    'balances': balances
                }, '足夠')
            else:
                return (False, {
                    'hightBuyPrice': hightBuyPrice,
                    'lowSellPrice': lowSellPrice,
                    'tokenAmt': tokenAmt,
                    'bestPrice': bestPrice,
                    'balances': balances
                }, '不足夠')


# #############################################################################
class Trader(object):
    """
    操盤手 V 0.1
    """

    def __init__(self, tradeType: str, tradePair: str):
        # api token
        self.token = API.getToken()
        # 交易類別
        self.tradeType = tradeType
        # 交易貨幣兌
        self.tradePair = tradePair
        # 訂單token數量: 刷量每次單次token數量
        self.tokenAmt = BRUSH_TOKEN_NUM

    def queryOrder(self):
        """
        查詢未成交委託單
        """
        body = {
            "method": "order.query",
            "params": [self.token, 0, 100],
            "id": 0
        }
        res = requests.post(
            CONFIG.TRADE_URL,
            data=json.dumps(body),
            headers=HEADER_DATA,
        )
        orders = json.loads(res.text)
        return orders

    def signal_V1(self):
        """
        交易訊號處理
        """

        # 判斷如果尚有委託單，則不允許再送出
        queryOrder = self.queryOrder()
        queryTotal = int(queryOrder['result']['total'])
        #  买卖方向   1 卖  2 买
        if self.tradeType == 'buy':
            orderType = 2
        if self.tradeType == 'sell':
            orderType = 1
        # 是否可以交易: True(可以) / False(不可以)
        isCanTrade = False
        if queryTotal != 0:
            # print('有未成交單')
            tmpLst = []
            for item in queryOrder['result']['records']:
                # 委託類別
                queryType = int(item['side'])
                tmpLst.append(queryType)

            if orderType not in tmpLst:
                isCanTrade = True

        else:
            # print('沒有未成交單')
            isCanTrade = True

        # pp.pprint(queryOrder)
        return isCanTrade

    def buyOrder(self):
        """
        訂單: 委買單
        """

        moneyStatus = MoneyManage.isEnough(self.tradePair, self.tradeType,
                                           float(self.tokenAmt))
        # print(moneyStatus)
        # 交易訊號: True可交易 / False不可交易
        singleRs = self.signal_V1()
        if singleRs and moneyStatus[0]:

            # ################################################
            # 訂單token價格(委買單價格由這修改)
            # tokenPrice = float(moneyStatus[1]['lowSellPrice']) + 0.000001
            tokenPrice = ORDER_BUY_PRICE
            # ################################################

            # 訂單類型
            # 1: 賣
            # 2: 買
            orderType = 2
            body = {
                "method":
                "order.limit",
                "params": [
                    self.token,
                    self.tradePair,
                    orderType,
                    str(self.tokenAmt),
                    str(tokenPrice),
                    0,
                ],
                "id":
                0
            }
            res = requests.post(
                CONFIG.TRADE_URL,
                data=json.dumps(body),
                headers=HEADER_DATA,
            )
            orders = json.loads(res.text)
            print('==========================================')
            pp.pprint(orders)
            print(f'成功: 送出[委買單]: {tokenPrice}')
            print('==========================================')

        else:
            print('==========================================')
            print('Pass: 送出[委買單]')
            print('==========================================')

    def sellOrder(self):
        """
        訂單: 委賣單
        """

        moneyStatus = MoneyManage.isEnough(self.tradePair, self.tradeType,
                                           float(self.tokenAmt))

        # print(moneyStatus)
        # 交易訊號: True可交易 / False不可交易
        singleRs = self.signal_V1()
        if singleRs and moneyStatus[0]:

            # ################################################
            # 訂單token價格(委賣單價格由這修改)
            # tokenPrice = float(moneyStatus[1]['lowSellPrice']) - 0.000001
            tokenPrice = ORDER_SELL_PRICE
            # ################################################

            # 訂單類型
            # 1: 賣
            # 2: 買
            orderType = 1
            body = {
                "method":
                "order.limit",
                "params": [
                    self.token,
                    self.tradePair,
                    orderType,
                    str(self.tokenAmt),
                    str(tokenPrice),
                    0,
                ],
                "id":
                0
            }
            res = requests.post(
                CONFIG.TRADE_URL,
                data=json.dumps(body),
                headers=HEADER_DATA,
            )
            orders = json.loads(res.text)
            print('==========================================')
            pp.pprint(orders)
            print(f'成功: 送出[委賣單]: {tokenPrice}')
            print('==========================================')

        else:
            print('==========================================')
            print('Pass: 送出[委賣單]')
            print('==========================================')

    def order(self):
        """
        下單
        """

        # 委買單
        if self.tradeType == 'buy':
            self.buyOrder()
        # 委賣單
        if self.tradeType == 'sell':
            self.sellOrder()


def startTrade(type: str):
    if type == 'buy':
        num = 1
        while num <= BRUSH_NUM:
            trader = Trader('buy', 'LVE/ETH')
            trader.order()
            print('buy')
            print(num)
            num += 1
            time.sleep(TRADE_SLEEP_TIME)

    if type == 'sell':
        num = 1
        while num <= BRUSH_NUM:
            trader = Trader('sell', 'LVE/ETH')
            trader.order()
            print('sell')
            print(num)
            num += 1
            time.sleep(TRADE_SLEEP_TIME)


if __name__ == "__main__":

    # 多進程Trader
    p = Pool()
    for i in range(2):
        if i == 0:
            p.apply_async(startTrade, args=('buy', ))
        if i == 1:
            p.apply_async(startTrade, args=('sell', ))

    print('操盤手: 多進程運行中....')
    p.close()
    p.join()
    print('操盤手: 多進程運行結束....')
