import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional
from indicators.technical_indicators import TechnicalIndicators


class VisualizationUtils:
    
    @staticmethod
    def plot_price_with_indicators(
        df: pd.DataFrame,
        title: str = 'Price with Technical Indicators',
        figsize: tuple = (14, 10),
        save_path: Optional[str] = None
    ):
        fig, axes = plt.subplots(3, 1, figsize=figsize, sharex=True)
        
        axes[0].plot(df['日期'], df['收盘'], label='Close Price', linewidth=1.5, color='black')
        axes[0].plot(df['日期'], df['sma_20'], label='SMA 20', linewidth=1, color='orange', alpha=0.7)
        axes[0].plot(df['日期'], df['sma_60'], label='SMA 60', linewidth=1, color='blue', alpha=0.7)
        
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            axes[0].fill_between(
                df['日期'],
                df['bb_upper'],
                df['bb_lower'],
                alpha=0.2,
                color='gray',
                label='Bollinger Bands'
            )
        
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Price', fontsize=12)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        if 'macd_fast' in df.columns and 'macd_signal' in df.columns:
            axes[1].plot(df['日期'], df['macd_fast'], label='MACD', linewidth=1, color='red')
            axes[1].plot(df['日期'], df['macd_signal'], label='Signal', linewidth=1, color='blue')
            axes[1].bar(df['日期'], df['macd_hist'], label='Histogram', alpha=0.3, color='gray')
            axes[1].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
            axes[1].set_ylabel('MACD', fontsize=12)
            axes[1].legend(loc='upper left')
            axes[1].grid(True, alpha=0.3)
        
        if 'rsi' in df.columns:
            axes[2].plot(df['日期'], df['rsi'], label='RSI', linewidth=1, color='purple')
            axes[2].axhline(y=70, color='red', linestyle='--', linewidth=1, label='Overbought')
            axes[2].axhline(y=30, color='green', linestyle='--', linewidth=1, label='Oversold')
            axes[2].fill_between(df['日期'], 70, 100, alpha=0.1, color='red')
            axes[2].fill_between(df['日期'], 0, 30, alpha=0.1, color='green')
            axes[2].set_ylabel('RSI', fontsize=12)
            axes[2].set_xlabel('Date', fontsize=12)
            axes[2].legend(loc='upper left')
            axes[2].set_ylim(0, 100)
            axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_macd_signals(
        df: pd.DataFrame,
        title: str = 'MACD Strategy Signals',
        figsize: tuple = (14, 8),
        save_path: Optional[str] = None
    ):
        fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        axes[0].plot(df['日期'], df['收盘'], label='Close Price', linewidth=1.5, color='black')
        
        buy_signals = df[(df['macd_golden_cross'] == 1) & (df['macd_golden_cross'].shift(1) == 0)]
        sell_signals = df[(df['macd_death_cross'] == 1) & (df['macd_death_cross'].shift(1) == 0)]
        
        if not buy_signals.empty:
            axes[0].scatter(buy_signals['日期'], buy_signals['收盘'], 
                           marker='^', color='green', s=100, label='Buy Signal', zorder=5)
        
        if not sell_signals.empty:
            axes[0].scatter(sell_signals['日期'], sell_signals['收盘'], 
                           marker='v', color='red', s=100, label='Sell Signal', zorder=5)
        
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Price', fontsize=12)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(df['日期'], df['macd_fast'], label='MACD', linewidth=1, color='red')
        axes[1].plot(df['日期'], df['macd_signal'], label='Signal', linewidth=1, color='blue')
        axes[1].bar(df['日期'], df['macd_hist'], label='Histogram', alpha=0.3, color='gray')
        axes[1].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        
        if not buy_signals.empty:
            axes[1].scatter(buy_signals['日期'], buy_signals['macd_fast'], 
                           marker='^', color='green', s=100, zorder=5)
        
        if not sell_signals.empty:
            axes[1].scatter(sell_signals['日期'], sell_signals['macd_fast'], 
                           marker='v', color='red', s=100, zorder=5)
        
        axes[1].set_ylabel('MACD', fontsize=12)
        axes[1].set_xlabel('Date', fontsize=12)
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_bollinger_bands(
        df: pd.DataFrame,
        title: str = 'Bollinger Bands Strategy',
        figsize: tuple = (14, 8),
        save_path: Optional[str] = None
    ):
        fig, axes = plt.subplots(2, 1, figsize=figsize, sharex=True)
        
        axes[0].plot(df['日期'], df['收盘'], label='Close Price', linewidth=1.5, color='black')
        axes[0].plot(df['日期'], df['bb_upper'], label='Upper Band', linewidth=1, color='red', alpha=0.7)
        axes[0].plot(df['日期'], df['bb_middle'], label='Middle Band', linewidth=1, color='orange', alpha=0.7)
        axes[0].plot(df['日期'], df['bb_lower'], label='Lower Band', linewidth=1, color='green', alpha=0.7)
        
        axes[0].fill_between(
            df['日期'],
            df['bb_upper'],
            df['bb_lower'],
            alpha=0.2,
            color='gray'
        )
        
        upper_breaks = df[df['bb_upper_break'] == 1]
        lower_breaks = df[df['bb_lower_break'] == 1]
        
        if not upper_breaks.empty:
            axes[0].scatter(upper_breaks['日期'], upper_breaks['收盘'], 
                           marker='^', color='red', s=100, label='Upper Break', zorder=5)
        
        if not lower_breaks.empty:
            axes[0].scatter(lower_breaks['日期'], lower_breaks['收盘'], 
                           marker='v', color='green', s=100, label='Lower Break', zorder=5)
        
        axes[0].set_title(title, fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Price', fontsize=12)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        axes[1].plot(df['日期'], df['bb_position'], label='BB Position', linewidth=1, color='purple')
        axes[1].axhline(y=0.8, color='red', linestyle='--', linewidth=1, label='Overbought')
        axes[1].axhline(y=0.2, color='green', linestyle='--', linewidth=1, label='Oversold')
        axes[1].axhline(y=0.5, color='gray', linestyle='--', linewidth=0.5, label='Middle')
        axes[1].fill_between(df['日期'], 0.8, 1.0, alpha=0.1, color='red')
        axes[1].fill_between(df['日期'], 0.0, 0.2, alpha=0.1, color='green')
        axes[1].set_ylabel('BB Position', fontsize=12)
        axes[1].set_xlabel('Date', fontsize=12)
        axes[1].set_ylim(0, 1)
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def format_backtest_results(results: dict) -> str:
        output = []
        output.append("=" * 50)
        output.append("BACKTEST RESULTS")
        output.append("=" * 50)
        
        for key, value in results.items():
            if isinstance(value, float):
                if 'ratio' in key or 'rate' in key or 'return' in key or 'drawdown' in key:
                    output.append(f"{key.replace('_', ' ').title()}: {value:.4f}")
                else:
                    output.append(f"{key.replace('_', ' ').title()}: {value:.2f}")
            else:
                output.append(f"{key.replace('_', ' ').title()}: {value}")
        
        output.append("=" * 50)
        return "\n".join(output)


class DateUtils:
    
    @staticmethod
    def get_trading_days_back(days: int) -> str:
        from datetime import datetime, timedelta
        return (datetime.now() - timedelta(days=days + 20)).strftime('%Y%m%d')
    
    @staticmethod
    def get_today() -> str:
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d')
    
    @staticmethod
    def format_date(date_str: str, format: str = '%Y%m%d') -> str:
        from datetime import datetime
        return pd.to_datetime(date_str).strftime('%Y-%m-%d')


if __name__ == '__main__':
    from data.etf_data_fetcher import ETFDataFetcher
    
    fetcher = ETFDataFetcher()
    df = fetcher.get_etf_history('510300', '20230101', '20240201')
    
    df = TechnicalIndicators.calculate_all(df)
    
    viz = VisualizationUtils()
    viz.plot_price_with_indicators(df, title='沪深300ETF - 技术指标分析')
    viz.plot_macd_signals(df, title='沪深300ETF - MACD策略信号')
    viz.plot_bollinger_bands(df, title='沪深300ETF - 布林带策略')
