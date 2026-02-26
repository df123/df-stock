import pandas as pd
from typing import Dict, List, Optional
from data.etf_data_fetcher import ETFDataFetcher
from indicators.technical_indicators import TechnicalIndicators


class ETFScreener:
    
    def __init__(self, min_days: int = 60):
        self.fetcher = ETFDataFetcher()
        self.min_days = min_days
    
    def screen_by_macd(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        include_golden_cross: bool = True,
        include_death_cross: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
        
        etf_list = self.fetcher.get_etf_list()
        codes = etf_list['代码'].str.replace('[shsz]', '', regex=True).tolist()
        
        results = []
        
        for code in codes[:50]:
            try:
                df = self.fetcher.get_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                df = TechnicalIndicators.calculate_macd(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_golden_cross and latest_signals.get('macd_golden_cross'):
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'MACD Golden Cross',
                        'macd_fast': df.iloc[-1]['macd_fast'],
                        'macd_signal': df.iloc[-1]['macd_signal'],
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_death_cross and latest_signals.get('macd_death_cross'):
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'MACD Death Cross',
                        'macd_fast': df.iloc[-1]['macd_fast'],
                        'macd_signal': df.iloc[-1]['macd_signal'],
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_bollinger(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        include_upper_break: bool = True,
        include_lower_break: bool = False,
        include_squeeze: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
        
        etf_list = self.fetcher.get_etf_list()
        codes = etf_list['代码'].str.replace('[shsz]', '', regex=True).tolist()
        
        results = []
        
        for code in codes[:50]:
            try:
                df = self.fetcher.get_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_upper_break and latest_signals.get('bb_upper_break'):
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'BB Upper Break',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_lower_break and latest_signals.get('bb_lower_break'):
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'BB Lower Break',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_squeeze and latest_signals.get('bb_squeeze'):
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'BB Squeeze',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_combined(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        require_macd_golden: bool = True,
        require_bb_above_middle: bool = True
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y%m%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
        
        etf_list = self.fetcher.get_etf_list()
        codes = etf_list['代码'].str.replace('[shsz]', '', regex=True).tolist()
        
        results = []
        
        for code in codes[:50]:
            try:
                df = self.fetcher.get_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                df = TechnicalIndicators.calculate_macd(df)
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                latest_row = df.iloc[-1]
                
                macd_condition = not require_macd_golden or latest_signals.get('macd_golden_cross')
                bb_condition = not require_bb_above_middle or latest_signals.get('bb_position', 0.5) > 0.5
                
                if macd_condition and bb_condition:
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'Combined Signal',
                        'macd_fast': latest_row['macd_fast'],
                        'macd_signal': latest_row['macd_signal'],
                        'bb_upper': latest_row['bb_upper'],
                        'bb_middle': latest_row['bb_middle'],
                        'bb_lower': latest_row['bb_lower'],
                        'close': latest_row['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': latest_row['日期']
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_volume(
        self,
        min_volume_ratio: float = 2.0,
        lookback_days: int = 20
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y%m%d')
        
        etf_list = self.fetcher.get_etf_list()
        codes = etf_list['代码'].str.replace('[shsz]', '', regex=True).tolist()
        
        results = []
        
        for code in codes[:50]:
            try:
                df = self.fetcher.get_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                avg_volume = df['成交量'].iloc[-lookback_days:].mean()
                latest_volume = df['成交量'].iloc[-1]
                
                if latest_volume > avg_volume * min_volume_ratio:
                    results.append({
                        'code': code,
                        'name': etf_list[etf_list['代码'].str.contains(code)].iloc[0]['名称'] if len(etf_list[etf_list['代码'].str.contains(code)]) > 0 else '',
                        'signal_type': 'High Volume',
                        'latest_volume': latest_volume,
                        'avg_volume': avg_volume,
                        'volume_ratio': latest_volume / avg_volume,
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()


if __name__ == '__main__':
    screener = ETFScreener()
    
    print("=== MACD Golden Cross Screening ===")
    macd_results = screener.screen_by_macd(include_golden_cross=True, include_death_cross=False)
    print(macd_results)
    
    print("\n=== Bollinger Bands Upper Break Screening ===")
    bb_results = screener.screen_by_bollinger(include_upper_break=True)
    print(bb_results)
    
    print("\n=== Combined Signal Screening ===")
    combined_results = screener.screen_by_combined()
    print(combined_results)
    
    print("\n=== High Volume Screening ===")
    volume_results = screener.screen_by_volume()
    print(volume_results)
