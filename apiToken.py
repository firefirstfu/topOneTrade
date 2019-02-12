"""
API請求模組
"""
import time
import datetime
import random
import os, sys
import json
import hashlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pprint
pp = pprint.PrettyPrinter(width=41, compact=True)

import requests

import config as CONFIG
from models.apiToken import APIToken


def requestToken() -> str:
    """
    請求TOP.ONE Token Url
    """

    num = random.randint(100000, 999999)
    curtime = int(time.time())
    data = 'appkey=' + CONFIG.APP_KEY + '&random=' + str(num) + '&time=' + str(
        curtime)
    sha256 = hashlib.sha256()
    sha256.update(data.encode('utf-8'))
    signature = sha256.hexdigest()
    params = {
        'appid': CONFIG.APP_ID,
        'time': str(curtime),
        'random': num,
        'sig': signature
    }
    res = requests.get(CONFIG.TOKEN_REQUEST_URL, params=params)
    res = json.loads(res.text)
    try:
        token = res['data']['apitoken']
    except Exception as e:
        print(e)
        token = None
    return token


class API(object):
    """
    TOP.ONE Token API
    """

    @classmethod
    def getToken(cls) -> str:
        """
        取得Top.One api token
        """

        try:

            # 請求token Url
            token = cls.refreshToken()
        except Exception as e:
            print(e)
            token = None

        return token

    @classmethod
    def refreshToken(cls) -> str:
        """
        API請求頻率處理
        """

        tokens = APIToken.select().limit(1)
        # 沒有請求過，直接請求後寫入DB
        if len(tokens) == 0:
            # print('沒有請求過，直接請求後寫入DB')
            token = requestToken()
            if not None:
                tokenObj = APIToken()
                tokenObj.token = token
                tokenObj.requestTime = int(time.time())
                tokenObj.save()

        else:
            # 有請求過，判斷是否過期，如果過期重新請求後寫入DB
            # print('有請求過，判斷是否過期，如果過期重新請求後寫入DB')

            for token in tokens:
                _id = token.id
                _token = token.token
                _requestTime = token.requestTime
                _requestTime = datetime.datetime.fromtimestamp(_requestTime)

            # 現在時間
            nowTime = datetime.datetime.now()
            # 2小时后
            deltaTime = _requestTime + datetime.timedelta(hours=2)

            if nowTime >= deltaTime:
                _token = requestToken()
                APIToken.update(
                    token=_token, requestTime=int(
                        time.time())).where(APIToken.id == _id).execute()
                # print(f'Token: {_token}')
                # print(f'請求時間: {_requestTime}')
                # print(f'到期時間: {deltaTime}')

            return _token


if __name__ == "__main__":
    # token = API.refreshToken()
    # print(token)
    pass
