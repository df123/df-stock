import pandas as pd
import backtrader as bt


class BollingerBandsStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('position_size', 0.95),
        ('stop_loss', 0.05),
        ('take_profit', 0.10),
    )

    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.period,
            devfactor=self.p.devfactor
        )
        
        self.buy_price = None
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
            if self.data.close[0] > self.bb.lines.top[0]:
                self.buy(size=self.p.position_size)
                self.buy_price = self.data.close[0]
        else:
            if self.data.close[0] < self.bb.lines.bot[0]:
                self.sell(size=self.position.size)
            
            if self.buy_price:
                if self.data.close[0] >= self.buy_price * (1 + self.p.take_profit):
                    self.sell(size=self.position.size)
                elif self.data.close[0] <= self.buy_price * (1 - self.p.stop_loss):
                    self.sell(size=self.position.size)


class BBMeanReversionStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('position_size', 0.95),
        ('oversold_threshold', 0.2),
        ('overbought_threshold', 0.8),
    )

    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.period,
            devfactor=self.p.devfactor
        )
        
        bb_width = self.bb.lines.top - self.bb.lines.bot
        self.bb_position = (self.data.close - self.bb.lines.bot) / bb_width
        
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
            if self.bb_position[0] < self.p.oversold_threshold:
                self.buy(size=self.p.position_size)
        else:
            if self.bb_position[0] > self.p.overbought_threshold:
                self.sell(size=self.position.size)


class BBSqueezeStrategy(bt.Strategy):
    params = (
        ('period', 20),
        ('devfactor', 2.0),
        ('position_size', 0.95),
        ('squeeze_factor', 0.5),
    )

    def __init__(self):
        self.bb = bt.indicators.BollingerBands(
            self.data.close,
            period=self.p.period,
            devfactor=self.p.devfactor
        )
        
        self.bb_width = self.bb.lines.top - self.bb.lines.bot
        self.bb_width_sma = bt.indicators.SMA(self.bb_width, period=50)
        self.is_squeeze = self.bb_width < (self.bb_width_sma * self.p.squeeze_factor)
        
        self.sma = bt.indicators.SMA(self.data.close, period=self.p.period)
        
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
            if self.is_squeeze[0]:
                if self.data.close[0] > self.sma[0] and self.data.close[0] > self.bb.lines.mid[0]:
                    self.buy(size=self.p.position_size)
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell(size=self.position.size)


if __name__ == '__main__':
    from backtest.backtest_engine import BacktestEngine
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20220101', '20240201')
    
    engine = BacktestEngine()
    results, cerebro = engine.run_bb_backtest(df, strategy_type='breakthrough')
    
    print("=== Bollinger Bands Breakthrough Strategy Backtest Results ===")
    for key, value in results.items():
        print(f"{key}: {value}")
