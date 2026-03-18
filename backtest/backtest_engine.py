import pandas as pd
import backtrader as bt
from strategies.macd_strategy import MACDStrategy, EnhancedMACDStrategy
from strategies.bollinger_strategy import BollingerBandsStrategy, BBMeanReversionStrategy, BBSqueezeStrategy
from strategies.combined_strategy import CombinedStrategy, AggressiveCombinedStrategy, ConservativeCombinedStrategy


class TradeRecorder(bt.Strategy):
    """交易记录器策略"""
    params = (
        ('strategy_name', 'default'),
    )
    
    def __init__(self):
        self.trades = []
        self.current_position = None
        self.cash = None
    
    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.cash = self.broker.getcash()
                self.current_position = {
                    'type': '买入',
                    'date': self.data.datetime.date(0).strftime('%Y-%m-%d'),
                    'price': order.executed.price,
                    'size': order.executed.size,
                    'value': order.executed.price * order.executed.size,
                    'cash': self.cash
                }
            elif order.issell():
                if self.current_position:
                    self.current_position['exit_date'] = self.data.datetime.date(0).strftime('%Y-%m-%d')
                    self.current_position['exit_price'] = order.executed.price
                    self.current_position['exit_value'] = order.executed.price * order.executed.size
                    self.current_position['profit'] = self.current_position['exit_value'] - self.current_position['value']
                    self.current_position['profit_pct'] = (self.current_position['profit'] / self.current_position['value']) * 100
                    self.current_position['exit_cash'] = self.broker.getcash()
                    self.trades.append(self.current_position.copy())
                    self.current_position = None
    
    def get_trades(self):
        """获取所有交易记录"""
        return self.trades


class BacktestEngine:
    
    def __init__(
        self,
        initial_cash: float = 100000,
        commission: float = 0.0003
    ):
        self.initial_cash = initial_cash
        self.commission = commission
    
    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['日期'])
        df.set_index('datetime', inplace=True)
        df = df.sort_index()
        df = df.rename(columns={
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
        })
        return df
    
    def run_backtest(
        self,
        df: pd.DataFrame,
        strategy_class: bt.Strategy,
        strategy_params: dict = None,
        strategy_name: str = 'unknown'
    ):
        df = self.prepare_data(df)
        
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
        
        if strategy_params:
            cerebro.addstrategy(strategy_class, **strategy_params)
        else:
            cerebro.addstrategy(strategy_class)
        
        cerebro.broker.setcash(self.initial_cash)
        cerebro.broker.setcommission(commission=self.commission)
        
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
        results = cerebro.run()
        strat = results[0]
        
        analyzer_results = self._extract_analytics(strat, cerebro)
        
        try:
            analyzer_results['trades_list'] = strat.get_trades_log()
        except (KeyError, TypeError, AttributeError, Exception):
            analyzer_results['trades_list'] = []
        
        return analyzer_results, cerebro
    
    def _extract_analytics(self, strat, cerebro):
        results = {
            'initial_cash': self.initial_cash,
            'final_value': cerebro.broker.getvalue(),
            'total_return': (cerebro.broker.getvalue() - self.initial_cash) / self.initial_cash,
        }
        
        try:
            results['sharpe_ratio'] = strat.analyzers.sharpe.get_analysis()['sharperatio']
        except (KeyError, TypeError, AttributeError, Exception):
            results['sharpe_ratio'] = None
        
        try:
            dd = strat.analyzers.drawdown.get_analysis()
            results['max_drawdown'] = dd['max']['drawdown']
            results['max_drawdown_money'] = dd['max']['moneydown']
        except (KeyError, TypeError, AttributeError, Exception):
            results['max_drawdown'] = None
            results['max_drawdown_money'] = None
        
        try:
            trades = strat.analyzers.trades.get_analysis()
            results['total_trades'] = trades['total']['total']
            results['won_trades'] = trades['won']['total']
            results['lost_trades'] = trades['lost']['total']
            if trades['total']['total'] > 0:
                results['win_rate'] = trades['won']['total'] / trades['total']['total']
            else:
                results['win_rate'] = 0
        except (KeyError, TypeError, AttributeError, Exception):
            results['total_trades'] = 0
            results['won_trades'] = 0
            results['lost_trades'] = 0
            results['win_rate'] = 0
        
        return results
    
    def run_macd_backtest(
        self,
        df: pd.DataFrame,
        strategy_type: str = 'basic',
        **params
    ):
        if strategy_type == 'basic':
            return self.run_backtest(df, MACDStrategy, params)
        elif strategy_type == 'enhanced':
            return self.run_backtest(df, EnhancedMACDStrategy, params)
    
    def run_bb_backtest(
        self,
        df: pd.DataFrame,
        strategy_type: str = 'breakthrough',
        **params
    ):
        strategy_map = {
            'breakthrough': BollingerBandsStrategy,
            'mean_reversion': BBMeanReversionStrategy,
            'squeeze': BBSqueezeStrategy
        }
        
        strategy_class = strategy_map.get(strategy_type, BollingerBandsStrategy)
        return self.run_backtest(df, strategy_class, params)
    
    def run_combined_backtest(
        self,
        df: pd.DataFrame,
        strategy_type: str = 'standard',
        **params
    ):
        strategy_map = {
            'standard': CombinedStrategy,
            'aggressive': AggressiveCombinedStrategy,
            'conservative': ConservativeCombinedStrategy
        }
        
        strategy_class = strategy_map.get(strategy_type, CombinedStrategy)
        return self.run_backtest(df, strategy_class, params)
    
    def compare_strategies(
        self,
        df: pd.DataFrame,
        strategies: list = None
    ) -> pd.DataFrame:
        if strategies is None:
            strategies = [
                ('MACD Basic', 'macd', 'basic'),
                ('MACD Enhanced', 'macd', 'enhanced'),
                ('BB Breakthrough', 'bb', 'breakthrough'),
                ('BB Mean Reversion', 'bb', 'mean_reversion'),
                ('Combined Standard', 'combined', 'standard'),
                ('Combined Aggressive', 'combined', 'aggressive'),
                ('Combined Conservative', 'combined', 'conservative'),
            ]
        
        results_list = []
        
        for name, category, subtype in strategies:
            try:
                if category == 'macd':
                    results, _ = self.run_macd_backtest(df, subtype)
                elif category == 'bb':
                    results, _ = self.run_bb_backtest(df, subtype)
                elif category == 'combined':
                    results, _ = self.run_combined_backtest(df, subtype)
                else:
                    continue
                
                results['strategy_name'] = name
                results_list.append(results)
            except Exception as e:
                print(f"Error running {name}: {e}")
                continue
        
        if results_list:
            return pd.DataFrame(results_list)
        else:
            return pd.DataFrame()


if __name__ == '__main__':
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20220101', '20240201')
    
    engine = BacktestEngine()
    
    print("=== Single Strategy Backtest ===")
    results, _ = engine.run_combined_backtest(df, strategy_type='standard')
    for key, value in results.items():
        print(f"{key}: {value}")
    
    print("\n=== Strategy Comparison ===")
    comparison = engine.compare_strategies(df)
    print(comparison)
