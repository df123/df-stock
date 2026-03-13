"""
测试增量更新进度功能
"""
import sys
import time
sys.path.insert(0, '/home/df/df-stock')

from scripts.incremental_update import IncrementalUpdater


def test_progress_callback():
    """测试进度回调功能"""
    print("测试进度回调功能...")
    
    progress_updates = []
    
    def progress_callback(progress, message, current=None, total=None):
        progress_updates.append({
            'progress': progress,
            'message': message,
            'current': current,
            'total': total
        })
        print(f"进度: {progress}% - {message}")
    
    updater = IncrementalUpdater(progress_callback=progress_callback)
    
    codes = ['510300', '510500']
    print(f"\n更新 {len(codes)} 个ETF...")
    results = updater.update_all(codes, verbose=False)
    
    print(f"\n共收到 {len(progress_updates)} 个进度更新")
    
    # 验证进度更新
    assert len(progress_updates) == len(codes), f"应该收到 {len(codes)} 个进度更新"
    
    # 验证进度是递增的
    progresses = [p['progress'] for p in progress_updates]
    for i in range(1, len(progresses)):
        assert progresses[i] >= progresses[i-1], "进度应该是递增的"
    
    # 验证当前值和总数
    last_update = progress_updates[-1]
    assert last_update['current'] == len(codes), "最后的current应该等于总数"
    assert last_update['total'] == len(codes), "total应该等于代码数"
    
    print("\n✓ 进度回调功能测试通过")
    return progress_updates


def test_progress_values():
    """测试进度值的准确性"""
    print("\n测试进度值的准确性...")
    
    progress_updates = test_progress_callback()
    
    codes = ['510300', '510500']
    expected_progress = [50, 100]  # 1/2=50%, 2/2=100%
    
    actual_progress = [p['progress'] for p in progress_updates]
    
    for expected, actual in zip(expected_progress, actual_progress):
        assert expected == actual, f"期望进度 {expected}%, 实际 {actual}%"
    
    print("✓ 进度值准确性测试通过")


if __name__ == '__main__':
    print("=" * 50)
    print("测试增量更新进度功能")
    print("=" * 50)
    
    try:
        test_progress_callback()
        test_progress_values()
        
        print("\n" + "=" * 50)
        print("所有测试通过！")
        print("=" * 50)
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
