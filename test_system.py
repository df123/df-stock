#!/usr/bin/env python3
"""
ETF量化分析系统 - 测试脚本
验证各模块功能是否正常
"""

import sys
import traceback


def test_imports():
    """测试依赖包导入"""
    print("\n=== 测试依赖包导入 ===")
    try:
        import akshare
        print("✓ akshare")
    except ImportError:
        print("✗ akshare 未安装")
        return False
    
    try:
        import pandas
        print("✓ pandas")
    except ImportError:
        print("✗ pandas 未安装")
        return False
    
    try:
        import pandas_ta
        print("✓ pandas_ta")
    except ImportError:
        print("✗ pandas_ta 未安装")
        return False
    
    try:
        import backtrader
        print("✓ backtrader")
    except ImportError:
        print("✗ backtrader 未安装")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib")
    except ImportError:
        print("✗ matplotlib 未安装")
        return False
    
    return True


def test_data_fetcher():
    """测试数据获取模块"""
    print("\n=== 测试数据获取模块 ===")
    try:
        from data.etf_data_fetcher import ETFDataFetcher
        fetcher = ETFDataFetcher()
        
        etf_list = fetcher.get_etf_list()
        print(f"✓ 获取ETF列表成功，共 {len(etf_list)} 个ETF")
        
        if len(etf_list) > 0:
            first_code = etf_list.iloc[0]['代码']
            print(f"  第一个ETF代码: {first_code}")
            
            realtime = fetcher.get_etf_realtime()
            print(f"✓ 获取实时行情成功，共 {len(realtime)} 个ETF")
        
        return True
    except Exception as e:
        print(f"✗ 数据获取模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_technical_indicators():
    """测试技术指标模块"""
    print("\n=== 测试技术指标模块 ===")
    try:
        from data.etf_data_fetcher import ETFDataFetcher
        from indicators.technical_indicators import TechnicalIndicators
        
        fetcher = ETFDataFetcher()
        df = fetcher.get_etf_history('510300', '20240101', '20240201')
        
        if df.empty:
            print("✗ 获取历史数据失败")
            return False
        
        print(f"✓ 获取历史数据成功，共 {len(df)} 条记录")
        
        df = TechnicalIndicators.calculate_macd(df)
        print("✓ 计算MACD指标成功")
        
        df = TechnicalIndicators.calculate_bollinger_bands(df)
        print("✓ 计算布林带指标成功")
        
        df = TechnicalIndicators.calculate_rsi(df)
        print("✓ 计算RSI指标成功")
        
        signals = TechnicalIndicators.get_latest_signals(df)
        print(f"✓ 获取最新信号成功，共 {len(signals)} 个信号")
        
        return True
    except Exception as e:
        print(f"✗ 技术指标模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_strategies():
    """测试策略模块"""
    print("\n=== 测试策略模块 ===")
    try:
        from data.etf_data_fetcher import ETFDataFetcher
        from strategies.macd_strategy import run_macd_strategy
        from strategies.bollinger_strategy import run_bb_strategy
        from strategies.combined_strategy import run_combined_strategy
        
        fetcher = ETFDataFetcher()
        df = fetcher.get_etf_history('510300', '20240101', '20240201')
        
        if df.empty:
            print("✗ 获取历史数据失败")
            return False
        
        results_macd, _ = run_macd_strategy(df, strategy_type='basic')
        print("✓ MACD策略回测成功")
        
        results_bb, _ = run_bb_strategy(df, strategy_type='breakthrough')
        print("✓ 布林带策略回测成功")
        
        results_combined, _ = run_combined_strategy(df, strategy_type='standard')
        print("✓ 组合策略回测成功")
        
        return True
    except Exception as e:
        print(f"✗ 策略模块测试失败: {e}")
        traceback.print_exc()
        return False


def test_backtest_engine():
    """测试回测引擎"""
    print("\n=== 测试回测引擎 ===")
    try:
        from data.etf_data_fetcher import ETFDataFetcher
        from backtest.backtest_engine import BacktestEngine
        
        fetcher = ETFDataFetcher()
        df = fetcher.get_etf_history('510300', '20240101', '20240201')
        
        if df.empty:
            print("✗ 获取历史数据失败")
            return False
        
        engine = BacktestEngine()
        results, _ = engine.run_macd_backtest(df, strategy_type='basic')
        print("✓ MACD策略回测成功")
        
        comparison = engine.compare_strategies(df, strategies=[
            ('MACD Basic', 'macd', 'basic'),
            ('BB Breakthrough', 'bb', 'breakthrough'),
        ])
        
        if not comparison.empty:
            print(f"✓ 策略对比成功，共 {len(comparison)} 个策略")
        
        return True
    except Exception as e:
        print(f"✗ 回测引擎测试失败: {e}")
        traceback.print_exc()
        return False


def test_screener():
    """测试筛选模块"""
    print("\n=== 测试筛选模块 ===")
    try:
        from screening.stock_screener import ETFScreener
        
        screener = ETFScreener(min_days=60)
        
        print("注意: 筛选功能需要获取大量ETF数据，测试可能较慢")
        
        volume_results = screener.screen_by_volume(min_volume_ratio=1.5, lookback_days=20)
        if not volume_results.empty:
            print(f"✓ 放量筛选成功，找到 {len(volume_results)} 个ETF")
        
        return True
    except Exception as e:
        print(f"✗ 筛选模块测试失败: {e}")
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("ETF量化分析系统 - 功能测试")
    print("=" * 60)
    
    all_passed = True
    
    all_passed &= test_imports()
    
    if all_passed:
        all_passed &= test_data_fetcher()
        all_passed &= test_technical_indicators()
        all_passed &= test_strategies()
        all_passed &= test_backtest_engine()
        all_passed &= test_screener()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！系统可以正常使用。")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
