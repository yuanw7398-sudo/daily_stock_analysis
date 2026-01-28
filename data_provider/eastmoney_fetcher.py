import requests
import json
import time
from datetime import datetime

def fetch_eastmoney_stock(stock_code):
    """从东方财富获取个股行情数据（免费接口，纯函数版）"""
    # 区分沪市(6开头=1)、深市(3/0开头=0)
    market_code = "1" if stock_code.startswith("6") else "0"
    # 东方财富接口URL（字段包含收盘价、涨跌幅等核心数据）
    url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={market_code}.{stock_code}&fields=f43,f44,f45,f46,f47,f48,f51,f168"
    
    try:
        time.sleep(1)  # 避免接口访问频率限制
        response = requests.get(url, timeout=10)
        data = json.loads(response.text)["data"]
        
        if not data:  # 无数据返回时
            print(f"股票{stock_code}暂无数据")
            return None
        
        # 提取核心数据，返回和项目兼容的格式
        return {
            "code": stock_code,
            "close": data["f43"],       # 最新价
            "open": data["f44"],       # 开盘价
            "high": data["f45"],       # 最高价
            "low": data["f46"],        # 最低价
            "change_rate": data["f47"],# 涨跌幅(%)
            "change_amount": data["f48"],# 涨跌额
            "volume": data["f51"],     # 成交量
            "market_cap": data["f168"] / 100000000 if data["f168"] else 0, # 总市值(亿)
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"获取{stock_code}数据失败：{str(e)}")
        return None

def fetch_eastmoney_market():
    """获取大盘指数（上证、深证成指）"""
    # 大盘配置：{指数名: (代码, 市场标识)}
    market_config = {
        "上证指数": ("000001", "1"),
        "深证成指": ("399001", "0")
    }
    market_data = {}
    
    for name, (code, market) in market_config.items():
        url = f"https://push2.eastmoney.com/api/qt/index/get?secid={market}.{code}&fields=f43,f47"
        try:
            time.sleep(1)
            response = requests.get(url, timeout=10)
            data = json.loads(response.text)["data"]
            
            market_data[name] = {
                "point": data["f43"],       # 当前点数
                "change_rate": data["f47"]  # 涨跌幅(%)
            }
        except Exception as e:
            print(f"获取{name}失败：{str(e)}")
            market_data[name] = {"point": 0, "change_rate": 0}
    
    return market_data
