import akshare as ak
import pandas as pd
from datetime import datetime
from typing import Optional, List


class ETFDataFetcher:
    def __init__(self):
        pass

    def get_etf_list(self) -> pd.DataFrame:
        return ak.fund_etf_category_sina(symbol='ETF基金')

    def get_etf_realtime(self, symbol: Optional[str] = None) -> pd.DataFrame:
        df = ak.fund_etf_spot_em()
        if symbol:
            df = df[df['代码'] == symbol]
        return df

    def get_etf_history(
        self,
        symbol: str,
        start_date: str,
        end_date: Optional[str] = None,
        period: str = 'daily',
        adjust: str = ''
    ) -> pd.DataFrame:
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        
        df = ak.fund_etf_hist_em(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            adjust=adjust
        )
        return df

    def search_etf(self, keyword: str) -> pd.DataFrame:
        df = self.get_etf_list()
        result = df[df['名称'].str.contains(keyword, na=False)]
        return result

    def get_top_gainers(self, top_n: int = 10) -> pd.DataFrame:
        df = self.get_etf_realtime()
        df_sorted = df.sort_values('涨跌幅', ascending=False)
        return df_sorted.head(top_n)

    def get_top_losers(self, top_n: int = 10) -> pd.DataFrame:
        df = self.get_etf_realtime()
        df_sorted = df.sort_values('涨跌幅', ascending=True)
        return df_sorted.head(top_n)


if __name__ == '__main__':
    fetcher = ETFDataFetcher()
    
    print("=== ETF List Sample ===")
    etf_list = fetcher.get_etf_list()
    print(etf_list.head())
    
    print("\n=== Real-time Data Sample ===")
    realtime = fetcher.get_etf_realtime('510300')
    print(realtime)
    
    print("\n=== Historical Data Sample ===")
    history = fetcher.get_etf_history('510300', '20240101', '20240201')
    print(history.head())
    
    print("\n=== Top 5 Gainers ===")
    top_gainers = fetcher.get_top_gainers(5)
    print(top_gainers[['代码', '名称', '最新价', '涨跌幅']])
