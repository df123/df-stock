"""
配置文件
"""
import os

class Config:
    MACD_DEFAULT_FAST = 12
    MACD_DEFAULT_SLOW = 26
    MACD_DEFAULT_SIGNAL = 9
    
    BB_DEFAULT_PERIOD = 20
    BB_DEFAULT_STD = 2.0
    
    RSI_DEFAULT_PERIOD = 14
    
    DEFAULT_COMMISSION = 0.0003
    DEFAULT_INITIAL_CASH = 100000.0
    
    DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'etf_data.db')
    DB_ENABLED = True
