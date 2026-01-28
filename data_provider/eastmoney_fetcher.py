import requests
import json
import time
from datetime import datetime
from .base import BaseDataFetcher  # 继承项目基础数据类

class EastMoneyFetcher(BaseDataFetcher):
    def __init__(self):
        super().__init__()
        self.name = "eastmoney"  # 数据源名称
        self.priority = 1  # 优先级（低于Tushare，可按需调整）

    def fetch_stock_data(self, stock_code):
        """获取个股行情数据，适配项目接口"""
        # 区分沪市/深市
        market_code = "1" if stock_code.startswith("6") else "0"
        url = f"https://push2.eastmoney.com/api/qt/stock/get?secid={market_code}.{stock_code}&fields=f43,f44,f45,f46,f47,f48,f51,f168"
        
        try:
            time.sleep(1)  # 避免接口限制
            response = requests.get(url, timeout=10)
            data = json.loads(response.text)["data"]
            if not data:
                return None
            
            return {
                "code": stock_code,
                "close": data["f43"],
                "open": data["f44"],
                "high": data["f45"],
                "low": data["f46"],
                "change_rate": data["f47"],
                "change_amount": data["f48"],
                "volume": data["f51"],
                "market_cap": data["f168"] / 100000000,
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            self.logger.error(f"EastMoney fetch {stock_code} failed: {str(e)}")
            return None

    def fetch_market_data(self):
        """获取大盘数据"""
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
                    "point": data["f43"],
                    "change_rate": data["f47"]
                }
            except Exception as e:
                self.logger.error(f"EastMoney fetch {name} failed: {str(e)}")
                market_data[name] = {"point": 0, "change_rate": 0}
        
        return market_data
