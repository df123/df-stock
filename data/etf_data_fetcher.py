import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Optional, List
from config import Config


class ETFDataFetcher:
    """
    ETF数据获取类
    
    数据源说明：
    - ETF列表: 新浪财经
    - 历史数据: 新浪财经
    
    注意: 前端链接使用东方财富网站查看K线图
    """
    
    def __init__(self, db_manager=None):
        self._db_manager = db_manager
    
    def get_etf_list(self, save_to_db: bool = True) -> pd.DataFrame:
        """
        获取ETF列表
        数据源: 新浪财经
        """
        df = ak.fund_etf_category_sina(symbol='ETF基金')
        
        if save_to_db and self._db_manager:
            self._db_manager.save_etf_list(df)
        
        return df
    
    def get_etf_history(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        period: str = 'daily',
        adjust: str = '',
        save_to_db: bool = True
    ) -> pd.DataFrame:
        """
        获取ETF历史行情
        数据源: 新浪财经
        """
        # 新浪财经需要完整代码格式（如 sh510300）
        full_symbol = symbol
        if not symbol.startswith(('sh', 'sz', 'SH', 'SZ')):
            if symbol.startswith('5') or symbol.startswith('6'):
                full_symbol = f'sh{symbol}'
            else:
                full_symbol = f'sz{symbol}'
        
        try:
            df = ak.fund_etf_hist_sina(symbol=full_symbol)
            
            if df.empty:
                df = ak.fund_etf_hist_sina(symbol=symbol)
            
            # 列名映射（新浪财经返回英文列名，需要转换为中文）
            from utils.helpers import DB_TO_CN_COLUMNS
            
            if not df.empty:
                df = df.rename(columns=DB_TO_CN_COLUMNS)
                
                # 根据参数过滤日期范围
                if '日期' in df.columns:
                    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                    df = df.dropna(subset=['日期'])
                    
                    if start_date or end_date:
                        if start_date:
                            start_dt = pd.to_datetime(start_date, format='%Y%m%d')
                            df = df[df['日期'] >= start_dt]
                        if end_date:
                            end_dt = pd.to_datetime(end_date, format='%Y%m%d')
                            df = df[df['日期'] <= end_dt]
                    
                    df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
                
                # 保存到数据库
                if save_to_db and self._db_manager:
                    self._db_manager.save_etf_history(symbol, df)
            
            return df
        except Exception as e:
            print(f"获取历史数据失败: {e}")
            return pd.DataFrame()
    
    def search_etf(self, keyword: str) -> pd.DataFrame:
        """
        搜索ETF
        数据源: 新浪财经
        """
        df = self.get_etf_list()
        result = df[df['名称'].str.contains(keyword, na=False)]
        return result
    
if __name__ == '__main__':
    fetcher = ETFDataFetcher()
    
    print("=== ETF List Sample (Sina) ===")
    etf_list = fetcher.get_etf_list()
    print(f"Total ETFs: {len(etf_list)}")
    print(etf_list.head()[['代码', '名称', '最新价', '涨跌幅']].to_string(index=False))
    
    print("\n=== Historical Data Sample (Sina) ===")
    history = fetcher.get_etf_history('510300', '20240201', '20240226')
    print(f"History records: {len(history)}")
    if not history.empty:
        print(history.tail()[['日期', '收盘', '开盘', '最高', '最低', '成交量']].to_string(index=False))
