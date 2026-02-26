#!/usr/bin/env python3
"""
ETF量化分析系统 - 主程序入口
使用AKShare获取ETF数据，实现MACD+布林带等技术指标分析
"""

import argparse
import sys
import pandas as pd
from datetime import datetime

from data.etf_data_fetcher import ETFDataFetcher
from indicators.technical_indicators import TechnicalIndicators
from backtest.backtest_engine import BacktestEngine
from screening.stock_screener import ETFScreener
from strategies.macd_strategy import run_macd_strategy
from strategies.bollinger_strategy import run_bb_strategy
from strategies.combined_strategy import run_combined_strategy
from utils.helpers import VisualizationUtils, DateUtils


def handle_realtime(args):
    """实时行情查询"""
    fetcher = ETFDataFetcher()
    
    if args.symbol:
        print(f"\n=== ETF {args.symbol} 实时行情 ===")
        df = fetcher.get_etf_realtime(args.symbol)
        print(df.to_string())
    else:
        print("\n=== 所有ETF实时行情 ===")
        df = fetcher.get_etf_realtime()
        
        if args.top:
            print(f"\n=== 涨幅前{args.top}名 ===")
            top_gainers = fetcher.get_top_gainers(args.top)
            print(top_gainers[['代码', '名称', '最新价', '涨跌幅', '成交量']].to_string())
            
            print(f"\n=== 跌幅前{args.top}名 ===")
            top_losers = fetcher.get_top_losers(args.top)
            print(top_losers[['代码', '名称', '最新价', '涨跌幅', '成交量']].to_string())
        else:
            print(df[['代码', '名称', '最新价', '涨跌幅', '成交量']].head(20).to_string())
            print(f"\n总共 {len(df)} 个ETF")


def handle_history(args):
    """历史数据查询"""
    fetcher = ETFDataFetcher()
    
    if not args.symbol:
        print("错误: 请指定ETF代码")
        return
    
    end_date = args.end if args.end else DateUtils.get_today()
    
    print(f"\n=== ETF {args.symbol} 历史数据 ({args.start} ~ {end_date}) ===")
    df = fetcher.get_etf_history(args.symbol, args.start, end_date, period=args.period)
    
    print(df.tail(args.rows).to_string())
    
    if args.indicators:
        print("\n=== 技术指标 ===")
        df = TechnicalIndicators.calculate_all(df)
        
        signals = TechnicalIndicators.get_latest_signals(df)
        print(f"\n最新信号:")
        for key, value in signals.items():
            print(f"  {key}: {value}")
    
    if args.save:
        filename = f"{args.symbol}_history_{args.start}_{end_date}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n数据已保存到: {filename}")


def handle_indicators(args):
    """技术指标分析"""
    fetcher = ETFDataFetcher()
    
    if not args.symbol:
        print("错误: 请指定ETF代码")
        return
    
    end_date = args.end if args.end else DateUtils.get_today()
    
    print(f"\n=== ETF {args.symbol} 技术指标分析 ===")
    df = fetcher.get_etf_history(args.symbol, args.start, end_date)
    df = TechnicalIndicators.calculate_all(df)
    
    print(f"\n最近 {args.rows} 天数据及指标:")
    cols_to_show = ['日期', '收盘', '成交量', 'macd_fast', 'macd_signal', 
                    'bb_upper', 'bb_middle', 'bb_lower', 'rsi']
    available_cols = [col for col in cols_to_show if col in df.columns]
    print(df[available_cols].tail(args.rows).to_string())
    
    signals = TechnicalIndicators.get_latest_signals(df)
    print(f"\n最新交易信号:")
    for key, value in signals.items():
        signal_type = "买入信号" if value in [True, 1] else "卖出信号" if value in [False, 0] else "中性"
        print(f"  {key}: {value} ({signal_type})")
    
    if args.plot:
        viz = VisualizationUtils()
        if args.indicator == 'all':
            viz.plot_price_with_indicators(df, title=f'ETF {args.symbol} - 技术指标分析')
        elif args.indicator == 'macd':
            viz.plot_macd_signals(df, title=f'ETF {args.symbol} - MACD策略')
        elif args.indicator == 'bb':
            viz.plot_bollinger_bands(df, title=f'ETF {args.symbol} - 布林带策略')


def handle_screen(args):
    """ETF筛选"""
    screener = ETFScreener(min_days=args.min_days)
    
    print(f"\n=== ETF筛选 ({args.strategy}) ===")
    
    if args.strategy == 'macd':
        results = screener.screen_by_macd(
            lookback_days=args.lookback,
            include_golden_cross=True,
            include_death_cross=False
        )
        print(results.to_string())
    elif args.strategy == 'bb':
        results = screener.screen_by_bollinger(
            lookback_days=args.lookback,
            include_upper_break=True,
            include_lower_break=False
        )
        print(results.to_string())
    elif args.strategy == 'combined':
        results = screener.screen_by_combined(
            lookback_days=args.lookback,
            require_macd_golden=True,
            require_bb_above_middle=True
        )
        print(results.to_string())
    elif args.strategy == 'volume':
        results = screener.screen_by_volume(
            min_volume_ratio=args.volume_ratio,
            lookback_days=args.lookback
        )
        print(results.to_string())
    else:
        print("错误: 不支持的策略类型")
        return
    
    if args.save and not results.empty:
        filename = f"screening_{args.strategy}_{datetime.now().strftime('%Y%m%d')}.csv"
        results.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"\n筛选结果已保存到: {filename}")


def handle_backtest(args):
    """策略回测"""
    if not args.symbol:
        print("错误: 请指定ETF代码")
        return
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history(args.symbol, args.start, args.end)
    
    engine = BacktestEngine(
        initial_cash=args.initial_cash,
        commission=args.commission
    )
    
    print(f"\n=== 策略回测: {args.strategy} ===")
    print(f"标的: {args.symbol}")
    print(f"回测期间: {args.start} ~ {args.end}")
    print(f"初始资金: {args.initial_cash:,.2f}")
    print(f"手续费率: {args.commission:.4%}")
    print("-" * 50)
    
    if args.strategy == 'macd':
        results, cerebro = engine.run_macd_backtest(df, strategy_type='macd_type')
    elif args.strategy == 'bb':
        results, cerebro = engine.run_bb_backtest(df, strategy_type='bb_type')
    elif args.strategy == 'combined':
        results, cerebro = engine.run_combined_backtest(df, strategy_type='combined_type')
    elif args.strategy == 'compare':
        comparison = engine.compare_strategies(df)
        print("\n=== 策略对比 ===")
        print(comparison.to_string())
        if args.save:
            filename = f"strategy_comparison_{args.symbol}_{datetime.now().strftime('%Y%m%d')}.csv"
            comparison.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\n对比结果已保存到: {filename}")
        return
    else:
        print("错误: 不支持的策略类型")
        return
    
    viz = VisualizationUtils()
    print(viz.format_backtest_results(results))
    
    if args.plot:
        cerebro.plot(style='candlestick')
    
    if args.save:
        import json
        filename = f"backtest_{args.strategy}_{args.symbol}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n回测结果已保存到: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='ETF量化分析系统 - 使用AKShare获取ETF数据，实现MACD+布林带等技术指标分析',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --action realtime --symbol 510300           # 查询实时行情
  python main.py --action history --symbol 510300 --start 20230101  # 查询历史数据
  python main.py --action indicators --symbol 510300 --plot   # 技术指标分析
  python main.py --action screen --strategy macd                # MACD策略筛选
  python main.py --action backtest --strategy macd --symbol 510300  # MACD策略回测
  python main.py --action backtest --strategy compare --symbol 510300  # 策略对比回测
        """
    )
    
    parser.add_argument('--action', type=str, required=True,
                       choices=['realtime', 'history', 'indicators', 'screen', 'backtest'],
                       help='操作类型: realtime(实时), history(历史), indicators(指标), screen(筛选), backtest(回测)')
    
    parser.add_argument('--symbol', type=str, help='ETF代码，例如: 510300')
    parser.add_argument('--start', type=str, help='开始日期 (格式: YYYYMMDD)')
    parser.add_argument('--end', type=str, help='结束日期 (格式: YYYYMMDD)')
    parser.add_argument('--period', type=str, default='daily', choices=['daily', 'weekly', 'monthly'],
                       help='数据周期: daily(日线), weekly(周线), monthly(月线)')
    
    parser.add_argument('--rows', type=int, default=10, help='显示行数')
    parser.add_argument('--top', type=int, help='显示前N名涨跌幅')
    parser.add_argument('--indicators', action='store_true', help='计算技术指标')
    parser.add_argument('--plot', action='store_true', help='绘制图表')
    parser.add_argument('--save', action='store_true', help='保存结果到文件')
    
    parser.add_argument('--strategy', type=str, help='策略类型: macd, bb, combined, volume, compare')
    parser.add_argument('--indicator', type=str, default='all', choices=['all', 'macd', 'bb'],
                       help='显示的指标: all(全部), macd, bb')
    
    parser.add_argument('--lookback', type=int, default=60, help='回溯天数 (筛选用)')
    parser.add_argument('--min-days', type=int, default=60, help='最少交易天数 (筛选用)')
    parser.add_argument('--volume-ratio', type=float, default=2.0, help='成交量倍数 (筛选用)')
    
    parser.add_argument('--initial-cash', type=float, default=100000, help='回测初始资金')
    parser.add_argument('--commission', type=float, default=0.0003, help='手续费率')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'realtime':
            handle_realtime(args)
        elif args.action == 'history':
            handle_history(args)
        elif args.action == 'indicators':
            handle_indicators(args)
        elif args.action == 'screen':
            handle_screen(args)
        elif args.action == 'backtest':
            handle_backtest(args)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
