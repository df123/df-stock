import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Optional, List
from config import Config


class ETFDataFetcher:
    """
    ETF数据获取类
    
    数据源说明：
    - 实时行情: 同花顺（基金净值数据）
    - ETF列表: 新浪财经
    - 历史数据: 新浪财经
    
    注意: 不使用东方财富(东财)数据源
    由于其他数据源的限制，实时行情使用同花顺的基金净值数据
    """
    
    def __init__(self, db_manager=None):
        self._cache = {
            'realtime': None,
            'timestamp': None
        }
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
    
    def get_etf_realtime(self, symbol: Optional[str] = None, save_to_db: bool = True) -> pd.DataFrame:
        """
        获取ETF实时净值数据
        数据源: 同花顺（基金净值数据）
        
        注意: 同花顺返回的是基金净值数据，不是实时市场行情
        主要字段: 基金代码, 基金名称, 当前-单位净值, 增长率
        """
        if self._cache['realtime'] is None:
            try:
                df = ak.fund_etf_spot_ths()
                
                # 转换为统一的列名格式
                if not df.empty:
                    df = df.rename(columns={
                        '基金代码': '代码',
                        '基金名称': '名称',
                        '当前-单位净值': '最新价',
                        '增长率': '涨跌幅',
                        '增长值': '涨跌额',
                        '最新-交易日': '数据日期'
                    })
                    
                    # 将增长率从字符串转换为数值（如 "6.43" -> 6.43）
                    if '涨跌幅' in df.columns:
                        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
                    
                    if '最新价' in df.columns:
                        df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce')
                    
                    # 过滤掉非ETF数据
                    df = df[df['基金类型'] == '股票型']
                    
                    # 保存到数据库
                    if save_to_db and self._db_manager:
                        self._db_manager.save_etf_realtime(df)
                    
                    self._cache['realtime'] = df
                    self._cache['timestamp'] = datetime.now()
            except Exception as e:
                print(f"获取实时数据失败: {e}")
                return pd.DataFrame()
        
        df = self._cache['realtime'].copy() if self._cache['realtime'] is not None else pd.DataFrame()
        
        if symbol and not df.empty:
            df = df[df['代码'].astype(str).str.contains(str(symbol), na=False)]
        
        return df
    
    def get_etf_history(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        period: str = 'daily',
        adjust: str = '',
        save_to_db: bool = True
    ) -> pd.DataFrame:
        """
        获取ETF历史行情
        数据源: 新浪财经
        """
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
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
            column_mapping = {
                'date': '日期',
                'open': '开盘',
                'high': '最高',
                'low': '最低',
                'close': '收盘',
                'volume': '成交量',
                'amount': '成交额'
            }
            
            if not df.empty:
                df = df.rename(columns=column_mapping)
                
                # 过滤日期范围
                if '日期' in df.columns:
                    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')
                    df = df.dropna(subset=['日期'])
                    
                    start_dt = pd.to_datetime(start_date, format='%Y%m%d')
                    end_dt = pd.to_datetime(end_date, format='%Y%m%d')
                    
                    df = df[(df['日期'] >= start_dt) & (df['日期'] <= end_dt)]
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
    
    def get_top_gainers(self, top_n: int = 10) -> pd.DataFrame:
        """
        获取涨幅前N名
        数据源: 同花顺
        """
        df = self.get_etf_realtime()
        
        if not df.empty and '涨跌幅' in df.columns:
            df_sorted = df.sort_values('涨跌幅', ascending=False)
            return df_sorted.head(top_n)
        
        return pd.DataFrame()
    
    def get_top_losers(self, top_n: int = 10) -> pd.DataFrame:
        """
        获取跌幅前N名
        数据源: 同花顺
        """
        df = self.get_etf_realtime()
        
        if not df.empty and '涨跌幅' in df.columns:
            df_sorted = df.sort_values('涨跌幅', ascending=True)
            return df_sorted.head(top_n)
        
        return pd.DataFrame()
    
    def get_etf_dividend(self, symbol: str) -> pd.DataFrame:
        """
        获取ETF分红信息
        数据源: 新浪财经
        """
        full_symbol = symbol
        if not symbol.startswith(('sh', 'sz', 'SH', 'SZ')):
            if symbol.startswith('5') or symbol.startswith('6'):
                full_symbol = f'sh{symbol}'
            else:
                full_symbol = f'sz{symbol}'
        
        return ak.fund_etf_dividend_sina(symbol=full_symbol)
    
    def clear_cache(self):
        """清除缓存"""
        self._cache = {
            'realtime': None,
            'timestamp': None
        }


if __name__ == '__main__':
    fetcher = ETFDataFetcher()
    
    print("=== ETF List Sample (Sina) ===")
    etf_list = fetcher.get_etf_list()
    print(f"Total ETFs: {len(etf_list)}")
    print(etf_list.head()[['代码', '名称', '最新价', '涨跌幅']].to_string(index=False))
    
    print("\n=== Real-time Data Sample (Tonghuashun) ===")
    realtime = fetcher.get_etf_realtime()
    print(f"Total realtime quotes: {len(realtime)}")
    if not realtime.empty:
        print("\nTop 5 Gainers:")
        top_gainers = fetcher.get_top_gainers(5)
        print(top_gainers[['代码', '名称', '最新价', '涨跌幅']].to_string(index=False))
    
    print("\n=== Historical Data Sample (Sina) ===")
    history = fetcher.get_etf_history('510300', '20240201', '20240226')
    print(f"History records: {len(history)}")
    if not history.empty:
        print(history.tail()[['日期', '收盘', '开盘', '最高', '最低', '成交量']].to_string(index=False))
