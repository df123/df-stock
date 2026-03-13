"""
测试增量更新功能
"""
import sys
sys.path.insert(0, '/home/df/df-stock')

from data.database import DatabaseManager
from scripts.incremental_update import IncrementalUpdater


def test_get_latest_date():
    """测试获取最新日期"""
    print("测试获取最新日期...")
    db = DatabaseManager()
    
    # 测试510300
    latest = db.query_etf_history('510300')['date'].max()
    print(f"510300 最新日期: {latest}")
    assert latest is not None, "510300应该有数据"
    
    # 测试一个不存在的代码
    latest = db.query_etf_history('999999')
    assert latest.empty, "不存在的代码应该返回空DataFrame"
    
    print("✓ 获取最新日期测试通过\n")


def test_incremental_update():
    """测试增量更新功能"""
    print("测试增量更新功能...")
    
    updater = IncrementalUpdater()
    
    # 更新单个ETF
    print("测试更新单个ETF (510300)...")
    result = updater.update_single_etf('510300')
    print(f"结果: {result}")
    assert result['code'] == '510300', "代码应该为510300"
    assert 'status' in result, "结果应该包含status字段"
    print("✓ 更新单个ETF测试通过\n")
    
    # 更新多个ETF
    print("测试更新多个ETF...")
    codes = ['510300', '510500']
    results = updater.update_all(codes, verbose=False)
    print(f"结果: {results}")
    assert results['total_codes'] == 2, "应该更新2个代码"
    print("✓ 更新多个ETF测试通过\n")


def test_api_endpoints():
    """测试API端点"""
    print("测试API端点...")
    
    import requests
    
    base_url = "http://localhost:8000/api/db"
    
    # 测试状态端点
    response = requests.get(f"{base_url}/update/status")
    assert response.status_code == 200, "状态端点应该返回200"
    data = response.json()
    assert data['success'] == True, "应该返回success=true"
    print("✓ 状态端点测试通过")
    
    # 测试启动端点
    response = requests.post(f"{base_url}/update/incremental")
    assert response.status_code == 200, "启动端点应该返回200"
    data = response.json()
    assert data['success'] == True, "应该返回success=true"
    print("✓ 启动端点测试通过\n")


if __name__ == '__main__':
    print("=" * 50)
    print("测试增量更新功能")
    print("=" * 50)
    print()
    
    try:
        test_get_latest_date()
        test_incremental_update()
        # test_api_endpoints()  # 需要API服务运行
        
        print("=" * 50)
        print("所有测试通过！")
        print("=" * 50)
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
