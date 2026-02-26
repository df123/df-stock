#!/usr/bin/env python3
"""
ETF量化分析系统 - 快速使用示例
演示主要功能的使用方法
"""

from data.etf_data_fetcher import ETFDataFetcher
from indicators.technical_indicators import TechnicalIndicators
from backtest.backtest_engine import BacktestEngine
from screening.stock_screener import ETFScreener
from utils.helpers import VisualizationUtils, DateUtils


def example_1_realtime_data():
    """示例1: 获取实时行情"""
    print("\n" + "="*60)
    print("示例1: 获取ETF实时行情")
    print("="*60)
    
    fetcher = ETFDataFetcher()
    
    top_gainers = fetcher.get_top_gainers(5)
    print("涨幅前5名:")
    print(top_gainers[['代码', '名称', '最新价', '涨跌幅']])
    
    print("\n特定ETF实时行情 (510300 沪深300ETF):")
    etf_info = fetcher.get_etf_realtime('510300')
    print(etf_info[['代码', '名称', '最新价', '涨跌幅', '成交量']].to_string())


def example_2_technical_indicators():
    """示例2: 计算技术指标"""
    print("\n" + "="*60)
    print("示例2: 计算技术指标")
    print("="*60)
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20240101', '20240201')
    
    df = TechnicalIndicators.calculate_all(df)
    
    print("\n最新交易信号:")
    signals = TechnicalIndicators.get_latest_signals(df)
    for key, value in signals.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    
    print("\n最近5天技术指标:")
    cols = ['日期', '收盘', 'macd_fast', 'macd_signal', 'bb_upper', 'bb_lower', 'rsi']
    print(df[cols].tail(5))


def example_3_macd_backtest():
    """示例3: MACD策略回测"""
    print("\n" + "="*60)
    print("示例3: MACD策略回测")
    print("="*60)
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20230101', '20240201')
    
    engine = BacktestEngine(initial_cash=100000)
    results, _ = engine.run_macd_backtest(df, strategy_type='basic')
    
    print("\n回测结果:")
    print(f"  初始资金: ¥{results['initial_cash']:,.2f}")
    print(f"  最终资金: ¥{results['final_value']:,.2f}")
    print(f"  总收益率: {results['total_return']*100:.2f}%")
    print(f"  最大回撤: {results['max_drawdown']*100:.2f}%")
    print(f"  夏普比率: {results['sharpe_ratio']:.4f}")
    print(f"  总交易次数: {results['total_trades']}")
    print(f"  胜率: {results['win_rate']*100:.2f}%")


def example_4_strategy_comparison():
    """示例4: 策略对比"""
    print("\n" + "="*60)
    print("示例4: 多策略对比")
    print("="*60)
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20230101', '20240201')
    
    engine = BacktestEngine()
    
    comparison = engine.compare_strategies(df, strategies=[
        ('MACD Basic', 'macd', 'basic'),
        ('MACD Enhanced', 'macd', 'enhanced'),
        ('BB Breakthrough', 'bb', 'breakthrough'),
        ('BB Mean Reversion', 'bb', 'mean_reversion'),
        ('Combined Standard', 'combined', 'standard'),
        ('Combined Conservative', 'combined', 'conservative'),
    ])
    
    print("\n策略对比结果:")
    print(comparison[['strategy_name', 'total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']])


def example_5_etf_screening():
    """示例5: ETF筛选"""
    print("\n" + "="*60)
    print("示例5: ETF筛选")
    print("="*60)
    
    screener = ETFScreener(min_days=60)
    
    print("MACD金叉信号:")
    macd_signals = screener.screen_by_macd(
        lookback_days=60,
        include_golden_cross=True,
        include_death_cross=False
    )
    
    if not macd_signals.empty:
        print(macd_signals[['code', 'name', 'signal_type', 'close']].to_string())
    else:
        print("未找到符合条件的ETF")
    
    print("\n布林带突破信号:")
    bb_signals = screener.screen_by_bollinger(
        lookback_days=60,
        include_upper_break=True,
        include_lower_break=False
    )
    
    if not bb_signals.empty:
        print(bb_signals[['code', 'name', 'signal_type', 'close', 'bb_position']].to_string())
    else:
        print("未找到符合条件的ETF")


def example_6_visualization():
    """示例6: 可视化分析"""
    print("\n" + "="*60)
    print("示例6: 可视化分析")
    print("="*60)
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20230101', '20240201')
    df = TechnicalIndicators.calculate_all(df)
    
    viz = VisualizationUtils()
    
    print("生成图表...")
    
    import matplotlib
    matplotlib.use('Agg')
    
    viz.plot_price_with_indicators(
        df, 
        title='沪深300ETF - 技术指标分析',
        save_path='510300_indicators.png'
    )
    
    viz.plot_macd_signals(
        df,
        title='沪深300ETF - MACD策略信号',
        save_path='510300_macd.png'
    )
    
    viz.plot_bollinger_bands(
        df,
        title='沪深300ETF - 布林带策略',
        save_path='510300_bb.png'
    )
    
    print("图表已保存到当前目录")


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("ETF量化分析系统 - 快速使用示例")
    print("="*60)
    
    examples = [
        ("获取实时行情", example_1_realtime_data),
        ("计算技术指标", example_2_technical_indicators),
        ("MACD策略回测", example_3_macd_backtest),
        ("多策略对比", example_4_strategy_comparison),
        ("ETF筛选", example_5_etf_screening),
        ("可视化分析", example_6_visualization),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n运行所有示例...")
    
    try:
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n错误: {name} 执行失败: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("所有示例执行完毕！")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
