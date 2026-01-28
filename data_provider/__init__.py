# 导入各数据源类
from .tushare_fetcher import TushareFetcher
from .akshare_fetcher import AkshareFetcher
from .eastmoney_fetcher import EastMoneyFetcher  # 新增：导入东方财富类

# 注册数据源列表（EastMoney放第一位，优先使用）
DATA_FETCHERS = [
    EastMoneyFetcher(),
    TushareFetcher(),
    AkshareFetcher()
]

# 暴露对外的接口（保持原有逻辑）
__all__ = ["DATA_FETCHERS", "TushareFetcher", "AkshareFetcher", "EastMoneyFetcher"]
