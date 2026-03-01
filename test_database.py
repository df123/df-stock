#!/usr/bin/env python3
"""
测试数据库功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.database import DatabaseManager
from data.etf_data_fetcher import ETFDataFetcher


def test_database():
    """测试数据库基本功能"""
    print("=== 测试数据库功能 ===\n")
    
    # 1. 初始化数据库
    print("1. 初始化数据库...")
    db_manager = DatabaseManager()
    print("   ✓ 数据库初始化成功\n")
    
    # 2. 查看数据库统计信息
    print("2. 查看数据库统计信息...")
    stats = db_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # 3. 测试数据获取和保存
    print("3. 测试数据获取和保存...")
    fetcher = ETFDataFetcher(db_manager=db_manager)
    
    try:
        # 获取实时数据
        print("   正在获取实时数据...")
        realtime_df = fetcher.get_etf_realtime(save_to_db=True)
        print(f"   ✓ 获取到 {len(realtime_df)} 条实时数据")
        
        if not realtime_df.empty:
            print(f"   示例数据:\n{realtime_df.head(3)}\n")
            
            # 获取某个ETF的历史数据
            test_code = realtime_df.iloc[0]['代码']
            print(f"   正在获取 {test_code} 的历史数据...")
            history_df = fetcher.get_etf_history(test_code, '20240101', '20240226', save_to_db=True)
            print(f"   ✓ 获取到 {len(history_df)} 条历史数据")
            
            if not history_df.empty:
                print(f"   示例数据:\n{history_df.tail(3)}\n")
    except Exception as e:
        print(f"   ✗ 获取数据失败: {e}\n")
    
    # 4. 查询数据库中的数据
    print("4. 查询数据库中的数据...")
    
    # 查询实时数据
    realtime_from_db = db_manager.query_etf_realtime()
    print(f"   ✓ 数据库中有 {len(realtime_from_db)} 条实时数据")
    
    # 查询历史数据
    if not realtime_df.empty:
        test_code = realtime_df.iloc[0]['代码']
        history_from_db = db_manager.query_etf_history(test_code)
        print(f"   ✓ 数据库中有 {len(history_from_db)} 条历史数据 (代码: {test_code})")
    
    print()
    
    # 5. 导出数据测试
    print("5. 测试数据导出...")
    try:
        export_file = db_manager.export_to_csv('etf_realtime')
        print(f"   ✓ 实时数据已导出到: {export_file}")
        
        export_file = db_manager.export_to_csv('etf_history')
        print(f"   ✓ 历史数据已导出到: {export_file}")
    except Exception as e:
        print(f"   ✗ 导出失败: {e}")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_database()
