#!/usr/bin/env python3
"""
ETF量化分析系统 - 离线测试脚本
使用模拟数据测试各模块功能
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_mock_data(days=200):
    """生成模拟K线数据"""
    np.random.seed(42)
    
    base_price = 3.0
    dates = []
    prices = []
    
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d')
        dates.append(date)
        
        if i == 0:
            price = base_price
        else:
            change = np.random.normal(0, 0.02)
            price = prices[-1] * (1 + change)
            price = max(price, 1.0)
        
        prices.append(price)
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': [p * (1 + np.random.uniform(-0.01, 0.01)) for p in prices],
        '收盘': prices,
        '最高': [p * (1 + abs(np.random.uniform(0, 0.02))) for p in prices],
        '最低': [p * (1 - abs(np.random.uniform(0, 0.02))) for p in prices],
        '成交量': [np.random.randint(100000, 1000000) for _ in range(days)],
    })
    
    return df


def test_indicators():
    """测试技术指标模块"""
    print("\n=== 测试技术指标模块 ===")
    try:
        from indicators.technical_indicators import TechnicalIndicators
        
        df = generate_mock_data(200)
        print(f"✓ 生成模拟数据: {len(df)} 条记录")
        
        df = TechnicalIndicators.calculate_macd(df)
        print("✓ MACD指标计算成功")
        
        df = TechnicalIndicators.calculate_bollinger_bands(df)
        print("✓ 布林带指标计算成功")
        
        df = TechnicalIndicators.calculate_rsi(df)
        print("✓ RSI指标计算成功")
        
        df = TechnicalIndicators.calculate_sma(df)
        print("✓ SMA指标计算成功")
        
        df = TechnicalIndicators.calculate_ema(df)
        print("✓ EMA指标计算成功")
        
        df = TechnicalIndicators.calculate_all(df)
        print("✓ 所有指标计算成功")
        
        signals = TechnicalIndicators.get_latest_signals(df)
        print(f"✓ 获取最新信号: {len(signals)} 个")
        
        print("\n最新信号状态:")
        for key, value in signals.items():
            status = "✓" if value else "✗"
            print(f"  {status} {key}: {value}")
        
        print("\n最后5天数据:")
        cols = ['日期', '收盘', 'macd_fast', 'macd_signal', 'bb_upper', 'bb_lower', 'rsi']
        print(df[cols].tail(5))
        
        return True
    except Exception as e:
        print(f"✗ 技术指标模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_strategies():
    """测试策略模块"""
    print("\n=== 测试策略模块 ===")
    try:
        from strategies.macd_strategy import MACDStrategy
        from strategies.bollinger_strategy import BollingerBandsStrategy
        from strategies.combined_strategy import CombinedStrategy
        import backtrader as bt
        
        df = generate_mock_data(200)
        
        print(f"✓ 生成模拟数据: {len(df)} 条记录")
        
        df['datetime'] = pd.to_datetime(df['日期'])
        df.set_index('datetime', inplace=True)
        df = df.rename(columns={
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
        })
        
        cerebro = bt.Cerebro()
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        cerebro.addstrategy(MACDStrategy)
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(commission=0.0003)
        
        results = cerebro.run()
        print(f"✓ MACD策略回测完成，最终资金: ¥{cerebro.broker.getvalue():,.2f}")
        
        return True
    except Exception as e:
        print(f"✗ 策略模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backtest_engine():
    """测试回测引擎"""
    print("\n=== 测试回测引擎 ===")
    try:
        from backtest.backtest_engine import BacktestEngine
        
        df = generate_mock_data(200)
        print(f"✓ 生成模拟数据: {len(df)} 条记录")
        
        engine = BacktestEngine(initial_cash=100000)
        
        results, cerebro = engine.run_macd_backtest(df, strategy_type='basic')
        print(f"✓ MACD策略回测成功")
        print(f"  总收益率: {results['total_return']*100:.2f}%")
        print(f"  最终资金: ¥{results['final_value']:,.2f}")
        
        comparison = engine.compare_strategies(df)
        print(f"✓ 策略对比成功，共 {len(comparison)} 个策略")
        
        if not comparison.empty:
            print(comparison[['strategy_name', 'total_return', 'win_rate']])
        
        return True
    except Exception as e:
        print(f"✗ 回测引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization():
    """测试可视化模块"""
    print("\n=== 测试可视化模块 ===")
    try:
        from indicators.technical_indicators import TechnicalIndicators
        from utils.helpers import VisualizationUtils
        import matplotlib
        matplotlib.use('Agg')
        
        df = generate_mock_data(200)
        df = TechnicalIndicators.calculate_all(df)
        print(f"✓ 生成模拟数据并计算指标")
        
        viz = VisualizationUtils()
        
        viz.plot_price_with_indicators(
            df,
            title='测试 - 价格与指标',
            save_path='test_indicators.png'
        )
        print("✓ 生成价格指标图表")
        
        viz.plot_macd_signals(
            df,
            title='测试 - MACD信号',
            save_path='test_macd.png'
        )
        print("✓ 生成MACD信号图表")
        
        viz.plot_bollinger_bands(
            df,
            title='测试 - 布林带',
            save_path='test_bb.png'
        )
        print("✓ 生成布林带图表")
        
        return True
    except Exception as e:
        print(f"✗ 可视化模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 60)
    print("ETF量化分析系统 - 离线功能测试")
    print("=" * 60)
    
    print("\n使用模拟数据测试各模块功能...")
    
    all_passed = True
    
    all_passed &= test_indicators()
    all_passed &= test_strategies()
    all_passed &= test_backtest_engine()
    all_passed &= test_visualization()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ 所有测试通过！系统功能正常。")
        print("\n注意: 在线数据获取功能需要网络连接，")
        print("     当前测试使用模拟数据验证核心功能。")
    else:
        print("✗ 部分测试失败，请检查错误信息。")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
