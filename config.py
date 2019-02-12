APP_ID = ''
APP_KEY = ''

# 貨幣市場深度(最佳5檔)
DEPTH_NUM = 5
# 刷量次數
BRUSH_NUM = 4
# 刷量每次單次token數量(訂單token數量: 測試階段固定用5個token數量測單)
BRUSH_TOKEN_NUM = 10

# ######################################################
# 操盤手Bot委買價
# ORDER_BUY_PRICE = 0.002991
# # # 操盤手Bot委賣價
# ORDER_SELL_PRICE = 0.002990

# 委買價 = 委買價 - 1檔
# 委賣價 = 委買價 - 1檔
# 操盤手Bot委買價
ORDER_BUY_PRICE = 0.001299
# 操盤手Bot委賣價
ORDER_SELL_PRICE = 0.001299
# ######################################################

# 每次下單間隔休眠時間
TRADE_SLEEP_TIME = 1

# TOP.ONE token請求Url
TOKEN_REQUEST_URL = 'https://server.top.one/api/apiToken'
# TOP.ONE 交易請求Url
TRADE_URL = 'https://trade.top.one/'
# TOP.ONE 市場深度Url
MARKET_DEPTH_URL = 'https://depth.top.one/'
# TOP.ONE 歷史成交記錄
HISTORY_DEALS = 'https://trade.top.one/history/'
