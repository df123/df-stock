import pandas as pd
import pandas_ta as ta
from typing import Tuple, Dict


class TechnicalIndicators:
    
    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        price_col: str = '收盘',
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        if df.empty:
            return df
        
        if len(df) < slow + signal:
            return df
        
        close_prices = df[price_col]
        
        macd_result = ta.macd(close_prices, fast=fast, slow=slow, signal=signal)
        
        if macd_result is None:
            return df
        
        df['macd_fast'] = macd_result[f'MACD_{fast}_{slow}_{signal}']
        df['macd_signal'] = macd_result[f'MACDs_{fast}_{slow}_{signal}']
        df['macd_hist'] = macd_result[f'MACDh_{fast}_{slow}_{signal}']
        
        df['macd_golden_cross'] = (df['macd_fast'] > df['macd_signal']).astype(int)
        df['macd_death_cross'] = (df['macd_fast'] < df['macd_signal']).astype(int)
        
        df['macd_signal_above_zero'] = (df['macd_fast'] > 0).astype(int)
        
        return df

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        price_col: str = '收盘',
        length: int = 20,
        std: float = 2.0
    ) -> pd.DataFrame:
        if df.empty:
            return df
        
        if len(df) < length:
            return df
        
        close_prices = df[price_col]
        
        bbands_result = ta.bbands(close_prices, length=length, std=std)
        
        if bbands_result is None:
            return df
        
        df['bb_upper'] = bbands_result[f'BBU_{length}_{std}_{std}']
        df['bb_middle'] = bbands_result[f'BBM_{length}_{std}_{std}']
        df['bb_lower'] = bbands_result[f'BBL_{length}_{std}_{std}']
        df['bb_width'] = bbands_result[f'BBB_{length}_{std}_{std}']
        
        df['bb_position'] = (close_prices - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        df['bb_upper_break'] = (close_prices > df['bb_upper']).astype(int)
        df['bb_lower_break'] = (close_prices < df['bb_lower']).astype(int)
        
        df['bb_squeeze'] = (df['bb_width'] < df['bb_width'].rolling(50).mean() * 0.8).astype(int)
        
        return df

    @staticmethod
    def calculate_sma(
        df: pd.DataFrame,
        price_col: str = '收盘',
        periods: list = [5, 10, 20, 60]
    ) -> pd.DataFrame:
        if df.empty:
            return df
        
        for period in periods:
            df[f'sma_{period}'] = ta.sma(df[price_col], length=period)
        
        return df

    @staticmethod
    def calculate_ema(
        df: pd.DataFrame,
        price_col: str = '收盘',
        periods: list = [12, 26]
    ) -> pd.DataFrame:
        if df.empty:
            return df
        
        for period in periods:
            df[f'ema_{period}'] = ta.ema(df[price_col], length=period)
        
        return df

    @staticmethod
    def calculate_rsi(
        df: pd.DataFrame,
        price_col: str = '收盘',
        period: int = 14
    ) -> pd.DataFrame:
        if df.empty:
            return df
        
        df['rsi'] = ta.rsi(df[price_col], length=period)
        
        df['rsi_overbought'] = (df['rsi'] > 70).astype(int)
        df['rsi_oversold'] = (df['rsi'] < 30).astype(int)
        
        return df

    @staticmethod
    def calculate_all(
        df: pd.DataFrame,
        price_col: str = '收盘'
    ) -> pd.DataFrame:
        df = df.copy()
        
        df = TechnicalIndicators.calculate_macd(df, price_col)
        df = TechnicalIndicators.calculate_bollinger_bands(df, price_col)
        df = TechnicalIndicators.calculate_sma(df, price_col)
        df = TechnicalIndicators.calculate_ema(df, price_col)
        df = TechnicalIndicators.calculate_rsi(df, price_col)
        
        return df

    @staticmethod
    def get_latest_signals(df: pd.DataFrame) -> Dict:
        if df.empty:
            return {}
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        signals = {
            'macd_golden_cross': bool(latest.get('macd_golden_cross', 0) and not prev.get('macd_golden_cross', 0)),
            'macd_death_cross': bool(latest.get('macd_death_cross', 0) and not prev.get('macd_death_cross', 0)),
            'macd_above_signal': bool(latest.get('macd_fast', 0) > latest.get('macd_signal', 0)),
            'bb_upper_break': bool(latest.get('bb_upper_break', 0)),
            'bb_lower_break': bool(latest.get('bb_lower_break', 0)),
            'bb_squeeze': bool(latest.get('bb_squeeze', 0)),
            'bb_position': float(latest.get('bb_position', 0.5)),
            'rsi_overbought': bool(latest.get('rsi_overbought', 0)),
            'rsi_oversold': bool(latest.get('rsi_oversold', 0)),
        }
        
        return signals


if __name__ == '__main__':
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20230101', '20240201')
    
    df = TechnicalIndicators.calculate_all(df)
    
    print("=== Data with Technical Indicators ===")
    print(df.tail(10))
    
    print("\n=== Latest Signals ===")
    signals = TechnicalIndicators.get_latest_signals(df)
    for key, value in signals.items():
        print(f"{key}: {value}")
