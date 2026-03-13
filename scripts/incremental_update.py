"""
增量更新ETF历史数据
"""
import sys
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd

sys.path.insert(0, '/home/df/df-stock')

from data.database import DatabaseManager
from data.etf_data_fetcher import ETFDataFetcher
from config import Config


class IncrementalUpdater:
    """增量更新器"""
    
    def __init__(self, progress_callback=None):
        self.db_manager = DatabaseManager()
        self.fetcher = ETFDataFetcher(db_manager=self.db_manager)
        self.results = {
            'total_codes': 0,
            'updated_codes': 0,
            'new_records': 0,
            'failed_codes': [],
            'details': []
        }
        self.progress_callback = progress_callback
    
    def get_latest_date(self, code: str) -> Optional[str]:
        """
        获取指定ETF的最新日期
        Returns: 最新日期字符串 YYYY-MM-DD，如果没有数据返回None
        """
        df = self.db_manager.query_etf_history(code)
        
        if df.empty:
            return None
        
        return df['date'].max()
    
    def update_single_etf(self, code: str, max_days: int = 30) -> Dict[str, Any]:
        """
        更新单个ETF的数据
        Args:
            code: ETF代码
            max_days: 最多获取的天数
        Returns: 更新结果
        """
        latest_date = self.get_latest_date(code)
        
        if latest_date is None:
            return {
                'code': code,
                'status': 'no_data',
                'message': '数据库中没有历史数据',
                'new_records': 0
            }
        
        latest_dt = pd.to_datetime(latest_date)
        start_date = (latest_dt + timedelta(days=1)).strftime('%Y%m%d')
        end_date = datetime.now().strftime('%Y%m%d')
        
        if start_date > end_date:
            return {
                'code': code,
                'status': 'up_to_date',
                'message': '数据已是最新',
                'new_records': 0
            }
        
        try:
            df = self.fetcher.get_etf_history(
                symbol=code,
                start_date=start_date,
                end_date=end_date,
                period='daily',
                adjust='',
                save_to_db=True
            )
            
            if df.empty:
                return {
                    'code': code,
                    'status': 'no_new_data',
                    'message': '没有新数据',
                    'new_records': 0
                }
            
            return {
                'code': code,
                'status': 'success',
                'message': '更新成功',
                'new_records': len(df),
                'date_range': f"{start_date} ~ {end_date}"
            }
        except Exception as e:
            return {
                'code': code,
                'status': 'failed',
                'message': str(e),
                'new_records': 0
            }
    
    def update_all(self, codes: Optional[List[str]] = None, verbose: bool = True) -> Dict[str, Any]:
        """
        增量更新所有ETF
        Args:
            codes: 要更新的代码列表，如果为None则更新所有
            verbose: 是否打印详细信息
        Returns: 更新结果汇总
        """
        if codes is None:
            codes = self._get_all_codes()
        
        self.results['total_codes'] = len(codes)
        self.results['failed_codes'] = []
        self.results['details'] = []
        total_new_records = 0
        total = len(codes)
        
        for i, code in enumerate(codes, 1):
            progress = int((i / total) * 100)
            
            if self.progress_callback:
                self.progress_callback(
                    progress=progress,
                    message=f"正在更新 [{i}/{total}] {code}...",
                    current=i,
                    total=total
                )
            
            if verbose:
                print(f"[{i}/{total}] 正在更新 {code}...", end=' ')
            
            result = self.update_single_etf(code)
            self.results['details'].append(result)
            
            if result['status'] == 'success':
                self.results['updated_codes'] += 1
                new_records = result['new_records']
                total_new_records += new_records
                if verbose:
                    print(f"✓ 新增 {new_records} 条记录")
            elif result['status'] == 'up_to_date':
                if verbose:
                    print(f"○ 数据已是最新")
            elif result['status'] == 'no_data':
                if verbose:
                    print(f"✗ 无历史数据")
            elif result['status'] == 'no_new_data':
                if verbose:
                    print(f"○ 无新数据")
            else:
                self.results['failed_codes'].append(code)
                if verbose:
                    print(f"✗ 失败: {result['message']}")
        
        self.results['new_records'] = total_new_records
        
        if verbose:
            self._print_summary()
        
        return self.results
    
    def _get_all_codes(self) -> List[str]:
        """获取所有ETF代码"""
        df = self.db_manager.query_etf_list()
        codes = df['code'].unique().tolist()
        return codes
    
    def _print_summary(self):
        """打印更新摘要"""
        print("\n" + "="*50)
        print("增量更新完成")
        print("="*50)
        print(f"总ETF代码数: {self.results['total_codes']}")
        print(f"成功更新: {self.results['updated_codes']}")
        print(f"新增记录: {self.results['new_records']}")
        print(f"失败数量: {len(self.results['failed_codes'])}")
        
        if self.results['failed_codes']:
            print("\n失败的ETF代码:")
            for code in self.results['failed_codes']:
                print(f"  - {code}")
        print("="*50)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取更新摘要"""
        return {
            'total_codes': self.results['total_codes'],
            'updated_codes': self.results['updated_codes'],
            'new_records': self.results['new_records'],
            'failed_count': len(self.results['failed_codes']),
            'failed_codes': self.results['failed_codes'][:10]
        }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增量更新ETF历史数据')
    parser.add_argument('--codes', nargs='+', help='指定要更新的ETF代码')
    parser.add_argument('--quiet', action='store_true', help='静默模式，不打印详细信息')
    
    args = parser.parse_args()
    
    updater = IncrementalUpdater()
    
    if args.codes:
        print(f"更新指定的 {len(args.codes)} 个ETF代码...")
        updater.update_all(args.codes, verbose=not args.quiet)
    else:
        print("更新所有ETF...")
        updater.update_all(verbose=not args.quiet)
    
    return updater.get_summary()


if __name__ == '__main__':
    summary = main()
    print("\n结果摘要:", summary)
