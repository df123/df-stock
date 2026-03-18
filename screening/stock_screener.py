import pandas as pd
from typing import Dict, List, Optional
from data.etf_data_fetcher import ETFDataFetcher
from data.database.db_manager import DatabaseManager
from indicators.technical_indicators import TechnicalIndicators
import sqlite3


class ETFScreener:
    
    def __init__(self, min_days: int = 35):
        self.fetcher = ETFDataFetcher()
        self.db_manager = DatabaseManager()
        self.min_days = min_days
    
    def _get_all_codes(self, limit: int = 1000) -> List[str]:
        """获取所有ETF代码，去重处理带前缀和不带前缀的重复代码"""
        with self.db_manager._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT code FROM etf_history ORDER BY code")
            all_codes = [row[0] for row in cursor.fetchall()]
        
        seen = set()
        unique_codes = []
        
        for code in all_codes:
            normalized = code
            if code.startswith('sh') or code.startswith('sz'):
                normalized = code[2:]
            
            if normalized not in seen:
                seen.add(normalized)
                unique_codes.append(code)
        
        return unique_codes[:limit]
    
    def screen_by_macd(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        include_golden_cross: bool = True,
        include_death_cross: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        if end_date is None or end_date == '':
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (pd.to_datetime(end_date) - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        if not etf_list_df.empty:
            etf_name_map = etf_list_df.set_index('code')['name'].to_dict()
        else:
            etf_name_map = {}
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        codes = self._get_all_codes(1000)
        
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                
                from utils.helpers import DB_TO_CN_COLUMNS
                
                df = df.rename(columns=DB_TO_CN_COLUMNS)
                df = TechnicalIndicators.calculate_macd(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_golden_cross and latest_signals.get('macd_golden_cross'):
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'MACD Golden Cross',
                        'macd_fast': df.iloc[-1]['macd_fast'],
                        'macd_signal': df.iloc[-1]['macd_signal'],
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_death_cross and latest_signals.get('macd_death_cross'):
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'MACD Death Cross',
                        'macd_fast': df.iloc[-1]['macd_fast'],
                        'macd_signal': df.iloc[-1]['macd_signal'],
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                print(f"[ERROR] Error processing {code}: {e}")
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
        
        if end_date is None or end_date == '':
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (pd.to_datetime(end_date) - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        if not etf_list_df.empty:
            etf_name_map = etf_list_df.set_index('code')['name'].to_dict()
        else:
            etf_name_map = {}
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        codes = self._get_all_codes(1000)
        
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                
                from utils.helpers import DB_TO_CN_COLUMNS
                
                df = df.rename(columns=DB_TO_CN_COLUMNS)
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_upper_break and latest_signals.get('bb_upper_break'):
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'BB Upper Break',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_lower_break and latest_signals.get('bb_lower_break'):
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'BB Lower Break',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
                
                if include_squeeze and latest_signals.get('bb_squeeze'):
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'BB Squeeze',
                        'bb_upper': df.iloc[-1]['bb_upper'],
                        'bb_middle': df.iloc[-1]['bb_middle'],
                        'bb_lower': df.iloc[-1]['bb_lower'],
                        'close': df.iloc[-1]['收盘'],
                        'bb_position': latest_signals['bb_position'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                print(f"[ERROR] Error processing {code}: {e}")
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
        
        if end_date is None or end_date == '':
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (pd.to_datetime(end_date) - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        if not etf_list_df.empty:
            etf_name_map = etf_list_df.set_index('code')['name'].to_dict()
        else:
            etf_name_map = {}
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        codes = self._get_all_codes(1000)
        
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                
                from utils.helpers import DB_TO_CN_COLUMNS
                
                df = df.rename(columns=DB_TO_CN_COLUMNS)
                df = TechnicalIndicators.calculate_macd(df)
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                latest_row = df.iloc[-1]
                
                macd_condition = not require_macd_golden or latest_signals.get('macd_golden_cross')
                bb_condition = not require_bb_above_middle or latest_signals.get('bb_position', 0.5) > 0.5
                
                
                if macd_condition and bb_condition:
                    etf_name = etf_name_map.get(code, '')
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
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
                print(f"[ERROR] Error processing {code}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_volume(
        self,
        min_volume_ratio: float = 2.0,
        lookback_days: int = 20,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        
        if end_date is None or end_date == '':
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (pd.to_datetime(end_date) - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        if not etf_list_df.empty:
            etf_name_map = etf_list_df.set_index('code')['name'].to_dict()
        else:
            etf_name_map = {}
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        codes = self._get_all_codes(1000)
        
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                
                from utils.helpers import DB_TO_CN_COLUMNS
                
                df = df.rename(columns=DB_TO_CN_COLUMNS)
                
                avg_volume = df['成交量'].iloc[-lookback_days:].mean()
                latest_volume = df['成交量'].iloc[-1]
                
                if latest_volume > avg_volume * min_volume_ratio:
                    etf_name = etf_name_map.get(code, '')
                    
                    
                    results.append({
                        'code': code,
                        'name': etf_name,
                        'signal_type': 'High Volume',
                        'latest_volume': latest_volume,
                        'avg_volume': avg_volume,
                        'volume_ratio': latest_volume / avg_volume,
                        'close': df.iloc[-1]['收盘'],
                        'date': df.iloc[-1]['日期']
                    })
            except Exception as e:
                print(f"[ERROR] Error processing {code}: {e}")
                continue
        
        return pd.DataFrame(results) if results else pd.DataFrame()
