import pandas as pd
import backtrader as bt
from indicators.technical_indicators import TechnicalIndicators


class MACDStrategy(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('position_size', 0.95),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_above_zero = self.macd.macd > 0
        self.macd_hist = self.macd.macd - self.macd.signal
        
        self.trades_log = []
        self.current_trade = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            dt = self.data.datetime.date(0).strftime('%Y-%m-%d')
            price = order.executed.price
            size = order.executed.size
            value = order.executed.value
            
            if order.isbuy():
                self.current_trade = {
                    'buy_date': dt,
                    'buy_price': price,
                    'size': size,
                    'buy_value': value,
                    'type': '买入'
                }
            elif order.issell() and self.current_trade:
                self.current_trade['sell_date'] = dt
                self.current_trade['sell_price'] = price
                self.current_trade['sell_value'] = value
                self.current_trade['profit'] = value - self.current_trade['buy_value']
                self.current_trade['profit_pct'] = (value / self.current_trade['buy_value'] - 1) * 100
                self.trades_log.append(self.current_trade.copy())
                self.current_trade = None

    def get_trades_log(self):
        return self.trades_log

    def next(self):
        if not self.position:
            if self.crossover > 0 and self.macd_above_zero:
                self.buy(size=self.p.position_size)
        else:
            if self.crossover < 0:
                self.sell(size=self.position.size)


class EnhancedMACDStrategy(bt.Strategy):
    params = (
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('position_size', 0.95),
        ('use_macd_above_zero', True),
        ('use_volume_confirm', False),
        ('volume_factor', 1.2),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.fast_period,
            period_me2=self.p.slow_period,
            period_signal=self.p.signal_period
        )
        self.crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_above_zero = self.macd.macd > 0
        
        if self.p.use_volume_confirm:
            self.sma_volume = bt.indicators.SMA(self.data.volume, period=20)
        
        self.trades_log = []
        self.current_trade = None

    def notify_order(self, order):
        if order.status in [order.Completed]:
            dt = self.data.datetime.date(0).strftime('%Y-%m-%d')
            price = order.executed.price
            size = order.executed.size
            value = order.executed.value
            
            if order.isbuy():
                self.current_trade = {
                    'buy_date': dt,
                    'buy_price': price,
                    'size': size,
                    'buy_value': value,
                    'type': '买入'
                }
            elif order.issell() and self.current_trade:
                self.current_trade['sell_date'] = dt
                self.current_trade['sell_price'] = price
                self.current_trade['sell_value'] = value
                self.current_trade['profit'] = value - self.current_trade['buy_value']
                self.current_trade['profit_pct'] = (value / self.current_trade['buy_value'] - 1) * 100
                self.trades_log.append(self.current_trade.copy())
                self.current_trade = None

    def get_trades_log(self):
        return self.trades_log

    def next(self):
        if not self.position:
            buy_signal = self.crossover > 0
            
            if self.p.use_macd_above_zero:
                buy_signal = buy_signal and self.macd_above_zero
            
            if self.p.use_volume_confirm:
                buy_signal = buy_signal and (self.data.volume[0] > self.sma_volume[0] * self.p.volume_factor)
            
            if buy_signal:
                self.buy(size=self.p.position_size)
        else:
            if self.crossover < 0:
                self.sell(size=self.position.size)


def run_macd_strategy(
    df: pd.DataFrame,
    initial_cash: float = 100000,
    commission: float = 0.0003,
    strategy_type: str = 'basic'
):
    df = df.copy()
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
    
    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None,
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume'
    )
    
    cerebro.adddata(data)
    
    if strategy_type == 'basic':
        cerebro.addstrategy(MACDStrategy)
    elif strategy_type == 'enhanced':
        cerebro.addstrategy(EnhancedMACDStrategy)
    
    cerebro.broker.setcash(initial_cash)
    cerebro.broker.setcommission(commission=commission)
    
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
    
    results = cerebro.run()
    strat = results[0]
    
    analyzer_results = {
        'initial_cash': initial_cash,
        'final_value': cerebro.broker.getvalue(),
        'total_return': (cerebro.broker.getvalue() - initial_cash) / initial_cash,
    }
    
    try:
        analyzer_results['sharpe_ratio'] = strat.analyzers.sharpe.get_analysis()['sharperatio']
    except:
        analyzer_results['sharpe_ratio'] = None
    
    try:
        dd = strat.analyzers.drawdown.get_analysis()
        analyzer_results['max_drawdown'] = dd['max']['drawdown']
        analyzer_results['max_drawdown_money'] = dd['max']['moneydown']
    except:
        analyzer_results['max_drawdown'] = None
        analyzer_results['max_drawdown_money'] = None
    
    try:
        trades = strat.analyzers.trades.get_analysis()
        analyzer_results['total_trades'] = trades['total']['total']
        analyzer_results['won_trades'] = trades['won']['total']
        analyzer_results['lost_trades'] = trades['lost']['total']
        if trades['total']['total'] > 0:
            analyzer_results['win_rate'] = trades['won']['total'] / trades['total']['total']
        else:
            analyzer_results['win_rate'] = 0
    except:
        analyzer_results['total_trades'] = 0
        analyzer_results['won_trades'] = 0
        analyzer_results['lost_trades'] = 0
        analyzer_results['win_rate'] = 0
    
    return analyzer_results, cerebro


if __name__ == '__main__':
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20220101', '20240201')
    
    results, cerebro = run_macd_strategy(df)
    
    print("=== MACD Strategy Backtest Results ===")
    for key, value in results.items():
        print(f"{key}: {value}")
