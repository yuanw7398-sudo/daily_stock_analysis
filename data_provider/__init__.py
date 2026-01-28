# 原有数据源类导入（保留，不影响）
from .tushare_fetcher import TushareFetcher
from .akshare_fetcher import AkshareFetcher

# 新增：导入东方财富的纯函数
from .eastmoney_fetcher import fetch_eastmoney_stock, fetch_eastmoney_market

# 原有数据源列表（保留）
DATA_FETCHERS = [
    TushareFetcher(),
    AkshareFetcher()
]

# 导出所有可用的函数/类（新增东方财富函数）
__all__ = [
    "DATA_FETCHERS", "TushareFetcher", "AkshareFetcher",
    "fetch_eastmoney_stock", "fetch_eastmoney_market"
]
