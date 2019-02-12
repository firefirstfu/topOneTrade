### TOP.ONE api token請求
    ## The effective time of token is 2 hours.（token有效时长是2小时，请定时获取新token进行下单请求。)
    ## Interface frequency limit is 1 minute 1 translation.（该接口频率限制为1分钟1次。请勿频繁请求，否则将被屏蔽一小时。）

## TOP.ONE 下單請求
    #order(put order,cancel order) Interface limit is 1 minute 10 translation.（下单撤单接口频率限制为1秒2次。请勿频繁请求，否则将被屏蔽一小时。）


## 使用方式
1、建立SQLite資料庫儲存(儲存apiToken用): 進models目錄內，執行python3 apiToken.py
2、編輯配置檔: config.py
    1、修改: APP_ID
    2、修改: APP_KEY
    3、修改: BRUSH_NUM
    4、修改: BRUSH_TOKEN_NUM
    5、修改: ORDER_BUY_PRICE
    6、修改: ORDER_SELL_PRICE
3、運行操盤手程式: python3 trade.py