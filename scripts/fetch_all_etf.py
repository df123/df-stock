import sys
sys.path.insert(0, '/home/df/df-stock')

import pandas as pd
from datetime import datetime, timedelta
from data.etf_data_fetcher import ETFDataFetcher
from data.database.db_manager import DatabaseManager
from typing import Optional
import time

def fetch_all_etf_to_db(
    start_date: str = '20230101',
    end_date: Optional[str] = None,
    start_code: Optional[str] = None,
    delay_seconds: float = 0.5
):
    """
    获取所有ETF的历史数据并保存到数据库
    
    Args:
        start_date: 起始日期，格式YYYYMMDD
        end_date: 结束日期，格式YYYYMMDD，不填则今天
        start_code: 从某个代码开始（用于断点续传）
        delay_seconds: 每次请求之间的延迟（秒），避免API限流
    """
    import os
    os.environ['PYTHONUNBUFFERED'] = '1'
    
    from data.database.db_manager import DatabaseManager
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    
    print(f"开始获取所有ETF历史数据")
    print(f"时间范围: {start_date} - {end_date}")
    print(f"延迟: {delay_seconds}秒")
    
    db_manager = DatabaseManager()
    fetcher = ETFDataFetcher(db_manager=db_manager)
    
    etf_list = fetcher.get_etf_list()
    total_etf = len(etf_list)
    print(f"\nETF总数: {total_etf}")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    start_processing = False
    
    for i, row in etf_list.iterrows():
        code = row['代码']
        name = row['名称']
        
        if start_code and not start_processing:
            if code == start_code:
                start_processing = True
                print(f"\n从代码 {code} 开始继续...")
            else:
                skip_count += 1
                continue
        
        print(f"\n[{i+1}/{total_etf}] 处理: {code} - {name}")
        
        try:
            df = fetcher.get_etf_history(
                symbol=code,
                start_date=start_date,
                end_date=end_date,
                save_to_db=True
            )
            
            if df.empty:
                print(f"  ⚠ 获取数据为空")
                fail_count += 1
            else:
                print(f"  ✓ 成功获取 {len(df)} 条记录")
                success_count += 1
            
            time.sleep(delay_seconds)
            
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            fail_count += 1
            time.sleep(delay_seconds)
    
    print(f"\n{'='*60}")
    print(f"完成！")
    print(f"成功: {success_count}")
    print(f"失败: {fail_count}")
    print(f"跳过: {skip_count}")
    print(f"总计: {success_count + fail_count + skip_count}")
    print(f"{'='*60}")


if __name__ == '__main__':
    import sys
    
    start_date = '20230101'
    end_date = None
    start_code = None
    delay_seconds = 0.5
    
    if len(sys.argv) > 1:
        start_date = sys.argv[1]
    if len(sys.argv) > 2:
        end_date = sys.argv[2]
    if len(sys.argv) > 3:
        start_code = sys.argv[3]
    if len(sys.argv) > 4:
        delay_seconds = float(sys.argv[4])
    
    fetch_all_etf_to_db(
        start_date=start_date,
        end_date=end_date,
        start_code=start_code,
        delay_seconds=delay_seconds
    )
