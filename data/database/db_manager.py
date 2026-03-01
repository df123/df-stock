"""
数据库管理器 - 提供数据库操作的统一接口
"""
import sqlite3
import os
from typing import Optional, List, Dict, Any
import pandas as pd
from datetime import datetime
from pathlib import Path

from .models import (
    ETFListModel, ETFRealtimeModel, ETFHistoryModel,
    ScreeningResultsModel, BacktestResultsModel
)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etf_data.db')
        
        self.db_path = db_path
        self._ensure_db_dir()
        self.init_database()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute(ETFListModel.create_table_sql())
            cursor.execute(ETFRealtimeModel.create_table_sql())
            cursor.execute(ETFHistoryModel.create_table_sql())
            cursor.execute(ScreeningResultsModel.create_table_sql())
            cursor.execute(BacktestResultsModel.create_table_sql())
            
            conn.commit()
    
    def save_etf_list(self, df: pd.DataFrame) -> int:
        """
        保存ETF列表
        Returns: 保存的记录数
        """
        if df.empty:
            return 0
        
        records = []
        for _, row in df.iterrows():
            record = {
                'code': str(row.get('代码', '')),
                'name': str(row.get('名称', '')),
                'fund_type': str(row.get('基金类型', ''))
            }
            records.append(record)
        
        return self._batch_insert_or_replace(
            ETFListModel.TABLE_NAME,
            ETFListModel.get_columns(),
            records
        )
    
    def save_etf_realtime(self, df: pd.DataFrame, snapshot_date: str = None) -> int:
        """
        保存实时行情数据
        Returns: 保存的记录数
        """
        if df.empty:
            return 0
        
        records = ETFRealtimeModel.from_dataframe(df, snapshot_date)
        
        return self._batch_insert_or_replace(
            ETFRealtimeModel.TABLE_NAME,
            ETFRealtimeModel.get_columns(),
            records,
            conflict_columns=['code', 'snapshot_date']
        )
    
    def save_etf_history(self, code: str, df: pd.DataFrame) -> int:
        """
        保存历史行情数据
        Returns: 保存的记录数
        """
        if df.empty:
            return 0
        
        records = ETFHistoryModel.from_dataframe(code, df)
        
        return self._batch_insert_or_replace(
            ETFHistoryModel.TABLE_NAME,
            ETFHistoryModel.get_columns(),
            records,
            conflict_columns=['code', 'date']
        )
    
    def save_screening_results(self, strategy: str, df: pd.DataFrame, lookback_days: int = None) -> int:
        """
        保存筛选结果
        Returns: 保存的记录数
        """
        if df.empty:
            return 0
        
        records = ScreeningResultsModel.from_dataframe(strategy, df, lookback_days)
        
        return self._batch_insert(
            ScreeningResultsModel.TABLE_NAME,
            ScreeningResultsModel.get_columns(),
            records
        )
    
    def save_backtest_results(self, strategy: str, code: str, results: Dict[str, Any]) -> int:
        """
        保存回测结果
        Returns: 保存的记录数 (0或1)
        """
        record = BacktestResultsModel.from_dict(strategy, code, results)
        
        return self._batch_insert(
            BacktestResultsModel.TABLE_NAME,
            BacktestResultsModel.get_columns(),
            [record]
        )
    
    def _batch_insert(self, table: str, columns: List[str], records: List[Dict[str, Any]]) -> int:
        """批量插入数据"""
        if not records:
            return 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            placeholders = ', '.join(['?'] * len(columns))
            columns_str = ', '.join(columns)
            sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            
            count = 0
            for record in records:
                values = [record.get(col) for col in columns]
                try:
                    cursor.execute(sql, values)
                    count += 1
                except sqlite3.IntegrityError:
                    pass
            
            conn.commit()
            return count
    
    def _batch_insert_or_replace(self, table: str, columns: List[str], 
                                  records: List[Dict[str, Any]], 
                                  conflict_columns: List[str] = None) -> int:
        """批量插入或替换数据"""
        if not records:
            return 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            placeholders = ', '.join(['?'] * len(columns))
            columns_str = ', '.join(columns)
            
            if conflict_columns:
                conflict_str = ', '.join(conflict_columns)
                sql = f"INSERT OR REPLACE INTO {table} ({columns_str}) VALUES ({placeholders})"
            else:
                sql = f"INSERT OR REPLACE INTO {table} ({columns_str}) VALUES ({placeholders})"
            
            count = 0
            for record in records:
                values = [record.get(col) for col in columns]
                try:
                    cursor.execute(sql, values)
                    count += 1
                except sqlite3.IntegrityError as e:
                    print(f"插入失败: {e}")
            
            conn.commit()
            return count
    
    def query_etf_history(self, code: str, start_date: str = None, 
                          end_date: str = None) -> pd.DataFrame:
        """
        查询历史数据
        """
        query = "SELECT * FROM etf_history WHERE code = ?"
        params = [code]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date ASC"
        
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def query_etf_realtime(self, code: str = None, 
                           snapshot_date: str = None) -> pd.DataFrame:
        """
        查询实时行情数据
        """
        query = "SELECT * FROM etf_realtime WHERE 1=1"
        params = []
        
        if code:
            query += " AND code = ?"
            params.append(code)
        
        if snapshot_date:
            query += " AND snapshot_date = ?"
            params.append(snapshot_date)
        
        query += " ORDER BY snapshot_date DESC, snapshot_time DESC"
        
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def query_screening_results(self, strategy: str = None, 
                                code: str = None,
                                screen_date: str = None) -> pd.DataFrame:
        """
        查询筛选结果
        """
        query = "SELECT * FROM screening_results WHERE 1=1"
        params = []
        
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        
        if code:
            query += " AND code = ?"
            params.append(code)
        
        if screen_date:
            query += " AND screen_date = ?"
            params.append(screen_date)
        
        query += " ORDER BY screen_date DESC, screen_time DESC"
        
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def query_backtest_results(self, strategy: str = None, 
                               code: str = None) -> pd.DataFrame:
        """
        查询回测结果
        """
        query = "SELECT * FROM backtest_results WHERE 1=1"
        params = []
        
        if strategy:
            query += " AND strategy = ?"
            params.append(strategy)
        
        if code:
            query += " AND code = ?"
            params.append(code)
        
        query += " ORDER BY run_date DESC, run_time DESC"
        
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
            return df
    
    def export_to_csv(self, table: str, output_path: str = None, 
                     filters: Dict[str, Any] = None) -> str:
        """
        导出表数据到CSV
        Returns: 导出文件路径
        """
        query = f"SELECT * FROM {table}"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY id DESC"
        
        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{table}_export_{timestamp}.csv"
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        return output_path
    
    def get_stats(self) -> Dict[str, Any]:
        """获取数据库统计信息"""
        stats = {}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            tables = ['etf_list', 'etf_realtime', 'etf_history', 
                     'screening_results', 'backtest_results']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            cursor.execute("SELECT MIN(snapshot_date), MAX(snapshot_date) FROM etf_realtime")
            date_range = cursor.fetchone()
            stats['realtime_date_range'] = f"{date_range[0]} ~ {date_range[1]}"
            
            cursor.execute("SELECT MIN(date), MAX(date) FROM etf_history")
            date_range = cursor.fetchone()
            stats['history_date_range'] = f"{date_range[0]} ~ {date_range[1]}"
            
            cursor.execute("SELECT COUNT(DISTINCT code) FROM etf_history")
            unique_codes = cursor.fetchone()[0]
            stats['unique_history_codes'] = unique_codes
        
        return stats
