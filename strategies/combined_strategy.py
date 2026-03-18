import pandas as pd
import backtrader as bt


class CombinedStrategy(bt.Strategy):
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('position_size', 0.95),
        ('bb_above_middle', True),
        ('macd_above_zero', True),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        
        self.macd_crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_above_zero = self.macd.macd > 0
        
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.bb_period,
            devfactor=self.p.bb_dev
        )
        
        self.bb_above_middle = self.data.close > self.bb.lines.mid
        
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
            buy_signal = self.macd_crossover > 0
            
            if self.p.macd_above_zero:
                buy_signal = buy_signal and self.macd_above_zero
            
            if self.p.bb_above_middle:
                buy_signal = buy_signal and self.bb_above_middle
            
            if buy_signal:
                self.buy(size=self.p.position_size)
        else:
            sell_signal = self.macd_crossover < 0
            sell_signal = sell_signal or (self.data.close < self.bb.lines.bot)
            
            if sell_signal:
                self.sell(size=self.position.size)


class AggressiveCombinedStrategy(bt.Strategy):
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('position_size', 0.95),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        
        self.macd_crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_hist = self.macd.macd - self.macd.signal
        
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.bb_period,
            devfactor=self.p.bb_dev
        )
        
        self.bb_width = self.bb.lines.top - self.bb.lines.bot
        self.bb_width_sma = bt.indicators.SMA(self.bb_width, period=50)
        self.is_squeeze = self.bb_width < (self.bb_width_sma * 0.5)
        
        self.trend = bt.indicators.SMA(self.data.close, period=60)
        
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
            if self.is_squeeze[0] and self.macd_crossover > 0:
                if self.data.close[0] > self.trend[0]:
                    self.buy(size=self.p.position_size)
        else:
            if self.macd_crossover < 0:
                self.sell(size=self.position.size)


class ConservativeCombinedStrategy(bt.Strategy):
    params = (
        ('macd_fast', 12),
        ('macd_slow', 26),
        ('macd_signal', 9),
        ('bb_period', 20),
        ('bb_dev', 2.0),
        ('rsi_period', 14),
        ('position_size', 0.95),
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.p.macd_fast,
            period_me2=self.p.macd_slow,
            period_signal=self.p.macd_signal
        )
        
        self.macd_crossover = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.macd_above_zero = self.macd.macd > 0
        
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.bb_period,
            devfactor=self.p.bb_dev
        )
        
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        
        self.sma20 = bt.indicators.SMA(self.data.close, period=20)
        self.sma60 = bt.indicators.SMA(self.data.close, period=60)
        self.uptrend = self.sma20 > self.sma60
        
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
            buy_signal = (
                self.macd_crossover > 0 and
                self.macd_above_zero and
                self.uptrend and
                self.data.close[0] > self.sma20[0] and
                self.rsi[0] < 70 and
                self.rsi[0] > 30
            )
            
            if buy_signal:
                self.buy(size=self.p.position_size)
        else:
            sell_signal = (
                self.macd_crossover < 0 or
                not self.uptrend or
                self.rsi[0] > 75
            )
            
            if sell_signal:
                self.sell(size=self.position.size)


if __name__ == '__main__':
    from backtest.backtest_engine import BacktestEngine
    engine = BacktestEngine()
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20220101', '20240201')
    
    print("=== Standard Combined Strategy ===")
    results1, _ = engine.run_combined_backtest(df, strategy_type='standard')
    for key, value in results1.items():
        print(f"{key}: {value}")
    
    print("\n=== Aggressive Combined Strategy ===")
    results2, _ = engine.run_combined_backtest(df, strategy_type='aggressive')
    for key, value in results2.items():
        print(f"{key}: {value}")
    
    print("\n=== Conservative Combined Strategy ===")
    results3, _ = engine.run_combined_backtest(df, strategy_type='conservative')
    for key, value in results3.items():
        print(f"{key}: {value}")
