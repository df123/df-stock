"""
数据库表模型定义
"""
from datetime import datetime
from typing import Dict, Any, List, Optional
import pandas as pd


class ETFListModel:
    """ETF基本信息表"""
    
    TABLE_NAME = 'etf_list'
    
    @staticmethod
    def create_table_sql() -> str:
        return """
        CREATE TABLE IF NOT EXISTS etf_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            fund_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def get_columns() -> List[str]:
        return ['code', 'name', 'fund_type']


class ETFRealtimeModel:
    """实时行情快照表"""
    
    TABLE_NAME = 'etf_realtime'
    
    @staticmethod
    def create_table_sql() -> str:
        return """
        CREATE TABLE IF NOT EXISTS etf_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            name TEXT,
            price REAL,
            change_percent REAL,
            change_amount REAL,
            data_date TEXT,
            fund_type TEXT,
            snapshot_date TEXT NOT NULL,
            snapshot_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code, snapshot_date)
        )
        """
    
    @staticmethod
    def get_columns() -> List[str]:
        return ['code', 'name', 'price', 'change_percent', 'change_amount', 
                'data_date', 'fund_type', 'snapshot_date', 'snapshot_time']
    
    @staticmethod
    def from_dataframe(df: pd.DataFrame, snapshot_date: str = None) -> List[Dict[str, Any]]:
        if snapshot_date is None:
            snapshot_date = datetime.now().strftime('%Y-%m-%d')
        snapshot_time = datetime.now().strftime('%H:%M:%S')
        
        records = []
        for _, row in df.iterrows():
            record = {
                'code': str(row.get('代码', row.get('基金代码', ''))),
                'name': str(row.get('名称', row.get('基金名称', ''))),
                'price': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                'change_percent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                'change_amount': float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
                'data_date': str(row.get('数据日期', snapshot_date)),
                'fund_type': str(row.get('基金类型', '')),
                'snapshot_date': snapshot_date,
                'snapshot_time': snapshot_time
            }
            records.append(record)
        return records


class ETFHistoryModel:
    """历史行情表"""
    
    TABLE_NAME = 'etf_history'
    
    @staticmethod
    def create_table_sql() -> str:
        return """
        CREATE TABLE IF NOT EXISTS etf_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume REAL,
            amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code, date)
        )
        """
    
    @staticmethod
    def get_columns() -> List[str]:
        return ['code', 'date', 'open', 'high', 'low', 'close', 'volume', 'amount']
    
    @staticmethod
    def from_dataframe(code: str, df: pd.DataFrame) -> List[Dict[str, Any]]:
        records = []
        for _, row in df.iterrows():
            record = {
                'code': str(code),
                'date': str(row.get('日期', '')),
                'open': float(row.get('开盘', 0)) if pd.notna(row.get('开盘')) else None,
                'high': float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None,
                'low': float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None,
                'close': float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else None,
                'volume': float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else None,
                'amount': float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else None
            }
            records.append(record)
        return records


class ScreeningResultsModel:
    """筛选结果表"""
    
    TABLE_NAME = 'screening_results'
    
    @staticmethod
    def create_table_sql() -> str:
        return """
        CREATE TABLE IF NOT EXISTS screening_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            code TEXT NOT NULL,
            name TEXT,
            signal_type TEXT,
            price REAL,
            change_percent REAL,
            lookback_days INTEGER,
            additional_info TEXT,
            screen_date TEXT NOT NULL,
            screen_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def get_columns() -> List[str]:
        return ['strategy', 'code', 'name', 'signal_type', 'price', 'change_percent', 
                'lookback_days', 'additional_info', 'screen_date', 'screen_time']
    
    @staticmethod
    def from_dataframe(strategy: str, df: pd.DataFrame, lookback_days: int = None) -> List[Dict[str, Any]]:
        screen_date = datetime.now().strftime('%Y-%m-%d')
        screen_time = datetime.now().strftime('%H:%M:%S')
        
        records = []
        for _, row in df.iterrows():
            record = {
                'strategy': strategy,
                'code': str(row.get('代码', '')),
                'name': str(row.get('名称', '')),
                'signal_type': str(row.get('信号', '')) if '信号' in row else None,
                'price': float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                'change_percent': float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                'lookback_days': lookback_days,
                'additional_info': None,
                'screen_date': screen_date,
                'screen_time': screen_time
            }
            records.append(record)
        return records


class BacktestResultsModel:
    """回测结果表"""
    
    TABLE_NAME = 'backtest_results'
    
    @staticmethod
    def create_table_sql() -> str:
        return """
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            strategy TEXT NOT NULL,
            code TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT,
            initial_cash REAL,
            final_value REAL,
            total_return REAL,
            max_drawdown REAL,
            sharpe_ratio REAL,
            win_rate REAL,
            total_trades INTEGER,
            commission_rate REAL,
            run_date TEXT NOT NULL,
            run_time TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    
    @staticmethod
    def get_columns() -> List[str]:
        return ['strategy', 'code', 'start_date', 'end_date', 'initial_cash', 'final_value',
                'total_return', 'max_drawdown', 'sharpe_ratio', 'win_rate', 'total_trades',
                'commission_rate', 'run_date', 'run_time']
    
    @staticmethod
    def from_dict(strategy: str, code: str, results: Dict[str, Any]) -> Dict[str, Any]:
        run_date = datetime.now().strftime('%Y-%m-%d')
        run_time = datetime.now().strftime('%H:%M:%S')
        
        return {
            'strategy': strategy,
            'code': code,
            'start_date': results.get('开始日期', ''),
            'end_date': results.get('结束日期', ''),
            'initial_cash': float(results.get('初始资金', 0)),
            'final_value': float(results.get('最终价值', 0)),
            'total_return': float(results.get('总收益率', 0)),
            'max_drawdown': float(results.get('最大回撤', 0)),
            'sharpe_ratio': float(results.get('夏普比率', 0)),
            'win_rate': float(results.get('胜率', 0)),
            'total_trades': int(results.get('交易次数', 0)),
            'commission_rate': float(results.get('手续费率', 0)),
            'run_date': run_date,
            'run_time': run_time
        }
