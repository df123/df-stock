import pandas as pd
from typing import Dict, List, Optional
from data.etf_data_fetcher import ETFDataFetcher
from data.database.db_manager import DatabaseManager
from indicators.technical_indicators import TechnicalIndicators


class ETFScreener:
    
    def __init__(self, min_days: int = 30):
        self.fetcher = ETFDataFetcher()
        self.db_manager = DatabaseManager()
        self.min_days = min_days
    
    def screen_by_macd(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        include_golden_cross: bool = True,
        include_death_cross: bool = False
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        import sqlite3
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT code FROM etf_history ORDER BY code LIMIT 50")
        codes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"[DEBUG] screen_by_macd: {len(codes)} codes to process")
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                print(f"[DEBUG] Processing code {i+1}/{len(codes)}: {code}, {len(df)} rows")
                
                column_mapping = {
                    'date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'volume': '成交量',
                    'amount': '成交额'
                }
                
                df = df.rename(columns=column_mapping)
                df = TechnicalIndicators.calculate_macd(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_golden_cross and latest_signals.get('macd_golden_cross'):
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
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
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
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
        
        print(f"[DEBUG] screen_by_macd: Found {len(results)} results")
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
        import sqlite3
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT code FROM etf_history ORDER BY code LIMIT 50")
        codes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"[DEBUG] screen_by_bollinger: {len(codes)} codes to process")
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                print(f"[DEBUG] Processing code {i+1}/{len(codes)}: {code}, {len(df)} rows")
                
                column_mapping = {
                    'date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'volume': '成交量',
                    'amount': '成交额'
                }
                
                df = df.rename(columns=column_mapping)
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                
                if include_upper_break and latest_signals.get('bb_upper_break'):
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
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
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
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
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
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
        
        print(f"[DEBUG] screen_by_bollinger: Found {len(results)} results")
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_combined(
        self,
        end_date: Optional[str] = None,
        lookback_days: int = 60,
        require_macd_golden: bool = True,
        require_bb_above_middle: bool = True
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        import sqlite3
        
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        else:
            end_date = pd.to_datetime(end_date).strftime('%Y-%m-%d')
        
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT code FROM etf_history ORDER BY code LIMIT 50")
        codes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"[DEBUG] screen_by_combined: {len(codes)} codes to process")
        print(f"[DEBUG] screen_by_combined: start_date={start_date}, end_date={end_date}")
        print(f"[DEBUG] screen_by_combined: require_macd_golden={require_macd_golden}, require_bb_above_middle={require_bb_above_middle}")
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    print(f"[DEBUG] Skipping {code}: insufficient data ({len(df)} rows)")
                    continue
                
                print(f"[DEBUG] Processing code {i+1}/{len(codes)}: {code}, {len(df)} rows")
                
                column_mapping = {
                    'date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'volume': '成交量',
                    'amount': '成交额'
                }
                
                df = df.rename(columns=column_mapping)
                df = TechnicalIndicators.calculate_macd(df)
                df = TechnicalIndicators.calculate_bollinger_bands(df)
                
                latest_signals = TechnicalIndicators.get_latest_signals(df)
                latest_row = df.iloc[-1]
                
                macd_condition = not require_macd_golden or latest_signals.get('macd_golden_cross')
                bb_condition = not require_bb_above_middle or latest_signals.get('bb_position', 0.5) > 0.5
                
                print(f"[DEBUG] {code}: macd_condition={macd_condition}, bb_condition={bb_condition}")
                print(f"[DEBUG] {code}: macd_golden_cross={latest_signals.get('macd_golden_cross')}, bb_position={latest_signals.get('bb_position', 0.5)}")
                
                if macd_condition and bb_condition:
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
                    print(f"[DEBUG] MATCH FOUND: {code}")
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
        
        print(f"[DEBUG] screen_by_combined: Found {len(results)} results")
        return pd.DataFrame(results) if results else pd.DataFrame()
    
    def screen_by_volume(
        self,
        min_volume_ratio: float = 2.0,
        lookback_days: int = 20
    ) -> pd.DataFrame:
        from datetime import datetime, timedelta
        import sqlite3
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=lookback_days + 30)).strftime('%Y-%m-%d')
        
        etf_list_df = self.db_manager.query_etf_list()
        
        if etf_list_df.empty:
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT code FROM etf_history ORDER BY code LIMIT 50")
        codes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"[DEBUG] screen_by_volume: {len(codes)} codes to process")
        
        results = []
        
        for i, code in enumerate(codes):
            try:
                df = self.db_manager.query_etf_history(code, start_date, end_date)
                
                if df.empty or len(df) < self.min_days:
                    continue
                
                print(f"[DEBUG] Processing code {i+1}/{len(codes)}: {code}, {len(df)} rows")
                
                column_mapping = {
                    'date': '日期',
                    'open': '开盘',
                    'high': '最高',
                    'low': '最低',
                    'close': '收盘',
                    'volume': '成交量',
                    'amount': '成交额'
                }
                
                df = df.rename(columns=column_mapping)
                
                avg_volume = df['成交量'].iloc[-lookback_days:].mean()
                latest_volume = df['成交量'].iloc[-1]
                
                if latest_volume > avg_volume * min_volume_ratio:
                    name_row = etf_list_df[etf_list_df['code'] == code]
                    etf_name = name_row.iloc[0]['name'] if len(name_row) > 0 else ''
                    
                    print(f"[DEBUG] MATCH FOUND: {code} - volume ratio: {latest_volume/avg_volume:.2f}")
                    
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
        
        print(f"[DEBUG] screen_by_volume: Found {len(results)} results")
        return pd.DataFrame(results) if results else pd.DataFrame()
