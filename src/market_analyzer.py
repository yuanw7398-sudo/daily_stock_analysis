    def __init__(self, search_service: Optional[SearchService] = None, analyzer=None, market_data: Optional[dict] = None):
        """
        初始化大盘分析器
        
        Args:
            search_service: 搜索服务实例
            analyzer: AI分析器实例（用于调用LLM）
            market_data: 外部传入的大盘数据（如东方财富）（可选）
        """
        self.config = get_config()
        self.search_service = search_service
        self.analyzer = analyzer
        self.market_data = market_data  # 保存东方财富数据
        
    def get_market_overview(self) -> MarketOverview:
        """
        获取市场概览数据
        
        Returns:
            MarketOverview: 市场概览数据对象
        """
        today = datetime.now().strftime('%Y-%m-%d')
        overview = MarketOverview(date=today)
        
        # 1. 获取主要指数行情
        overview.indices = self._get_main_indices()
        
        # 2. 获取涨跌统计
        self._get_market_statistics(overview)
        
        # 3. 获取板块涨跌榜
        self._get_sector_rankings(overview)
        
        # 4. 获取北向资金（可选）
        # self._get_north_flow(overview)
        
        return overview

    def _call_akshare_with_retry(self, fn, name: str, attempts: int = 2):
        last_error: Optional[Exception] = None
        for attempt in range(1, attempts + 1):
            try:
                return fn()
            except Exception as e:
                last_error = e
                logger.warning(f"[大盘] {name} 获取失败 (attempt {attempt}/{attempts}): {e}")
                if attempt < attempts:
                    time.sleep(min(2 ** attempt, 5))
        logger.error(f"[大盘] {name} 最终失败: {last_error}")
        return None
    
    def _get_main_indices(self) -> List[MarketIndex]:
        """获取主要指数实时行情（优先使用外部传入的东方财富数据）"""
        indices = []
        
        # ========== 新增：优先使用东方财富传入的数据 ==========
        if self.market_data:
            logger.info("[大盘] 使用外部传入的东方财富大盘数据...")
            # 映射东方财富指数名到系统内部代码
            eastmoney_to_internal = {
                "上证指数": "sh000001",
                "深证成指": "sz399001"
            }
            
            for name, data in self.market_data.items():
                if name in eastmoney_to_internal:
                    code = eastmoney_to_internal[name]
                    # 构造MarketIndex对象
                    index = MarketIndex(
                        code=code,
                        name=name,
                        current=float(data['point']),  # 东方财富的当前点数
                        change_pct=float(data['change_rate']),  # 东方财富的涨跌幅
                        # 其他字段暂时用0填充（核心字段已覆盖）
                        change=0.0,
                        open=0.0,
                        high=0.0,
                        low=0.0,
                        prev_close=0.0,
                        volume=0.0,
                        amount=0.0
                    )
                    indices.append(index)
            logger.info(f"[大盘] 从东方财富获取到 {len(indices)} 个指数行情")
            return indices
        # ========== 东方财富数据使用结束 ==========
        
        # 原有逻辑（akshare/yfinance）作为降级方案
        try:
            logger.info("[大盘] 未传入外部数据，使用akshare获取主要指数实时行情...")
            
            # 使用 akshare 获取指数行情（新浪财经接口，包含深市指数）
            df = self._call_akshare_with_retry(ak.stock_zh_index_spot_sina, "指数行情", attempts=2)
            
            if df is not None and not df.empty:
                for code, name in self.MAIN_INDICES.items():
                    # 查找对应指数
                    row = df[df['代码'] == code]
                    if row.empty:
                        # 尝试带前缀查找
                        row = df[df['代码'].str.contains(code)]
                    
                    if not row.empty:
                        row = row.iloc[0]
                        index = MarketIndex(
                            code=code,
                            name=name,
                            current=float(row.get('最新价', 0) or 0),
                            change=float(row.get('涨跌额', 0) or 0),
                            change_pct=float(row.get('涨跌幅', 0) or 0),
                            open=float(row.get('今开', 0) or 0),
                            high=float(row.get('最高', 0) or 0),
                            low=float(row.get('最低', 0) or 0),
                            prev_close=float(row.get('昨收', 0) or 0),
                            volume=float(row.get('成交量', 0) or 0),
                            amount=float(row.get('成交额', 0) or 0),
                        )
                        # 计算振幅
                        if index.prev_close > 0:
                            index.amplitude = (index.high - index.low) / index.prev_close * 100
                        indices.append(index)

            # 如果 akshare 获取失败或为空，尝试使用 yfinance 兜底
            if not indices:
                logger.warning("[大盘] 国内源获取失败，尝试使用 Yfinance 兜底...")
                indices = self._get_indices_from_yfinance()

            logger.info(f"[大盘] 获取到 {len(indices)} 个指数行情")

        except Exception as e:
            logger.error(f"[大盘] 获取指数行情失败: {e}")
            # 异常时也尝试兜底
            if not indices:
                indices = self._get_indices_from_yfinance()

        return indices
