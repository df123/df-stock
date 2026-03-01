"""
Pydantic数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RealtimeData(BaseModel):
    """实时行情数据模型"""
    code: str = Field(..., description="ETF代码")
    name: str = Field(..., description="ETF名称")
    price: Optional[float] = Field(None, description="最新价")
    change_percent: Optional[float] = Field(None, description="涨跌幅(%)")
    change_amount: Optional[float] = Field(None, description="涨跌额")
    data_date: Optional[str] = Field(None, description="数据日期")
    
    class Config:
        from_attributes = True


class HistoryData(BaseModel):
    """历史数据模型"""
    code: str = Field(..., description="ETF代码")
    date: str = Field(..., description="日期")
    open: Optional[float] = Field(None, description="开盘价")
    high: Optional[float] = Field(None, description="最高价")
    low: Optional[float] = Field(None, description="最低价")
    close: Optional[float] = Field(None, description="收盘价")
    volume: Optional[float] = Field(None, description="成交量")
    amount: Optional[float] = Field(None, description="成交额")
    
    class Config:
        from_attributes = True


class IndicatorData(BaseModel):
    """技术指标数据模型"""
    date: str = Field(..., description="日期")
    close: Optional[float] = Field(None, description="收盘价")
    macd: Optional[float] = Field(None, description="MACD")
    macd_signal: Optional[float] = Field(None, description="MACD信号线")
    macd_hist: Optional[float] = Field(None, description="MACD柱状图")
    bb_upper: Optional[float] = Field(None, description="布林带上轨")
    bb_middle: Optional[float] = Field(None, description="布林带中轨")
    bb_lower: Optional[float] = Field(None, description="布林带下轨")
    rsi: Optional[float] = Field(None, description="RSI")
    
    class Config:
        from_attributes = True


class BacktestRequest(BaseModel):
    """回测请求模型"""
    symbol: str = Field(..., description="ETF代码")
    strategy: str = Field(..., description="策略类型: macd, bb, combined")
    start_date: str = Field(..., description="开始日期(YYYYMMDD)")
    end_date: Optional[str] = Field(None, description="结束日期(YYYYMMDD)")
    initial_cash: Optional[float] = Field(100000, description="初始资金")
    commission: Optional[float] = Field(0.0003, description="手续费率")


class BacktestResult(BaseModel):
    """回测结果模型"""
    strategy: str = Field(..., description="策略类型")
    code: str = Field(..., description="ETF代码")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    initial_cash: float = Field(..., description="初始资金")
    final_value: float = Field(..., description="最终价值")
    total_return: float = Field(..., description="总收益率(%)")
    max_drawdown: float = Field(..., description="最大回撤(%)")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    win_rate: Optional[float] = Field(None, description="胜率(%)")
    total_trades: int = Field(..., description="交易次数")


class ScreeningRequest(BaseModel):
    """筛选请求模型"""
    strategy: str = Field(..., description="策略类型: macd, bb, combined, volume")
    lookback_days: Optional[int] = Field(60, description="回溯天数")
    min_days: Optional[int] = Field(60, description="最少交易天数")
    volume_ratio: Optional[float] = Field(2.0, description="成交量倍数")


class DatabaseStats(BaseModel):
    """数据库统计信息"""
    etf_list: int = Field(..., description="ETF列表记录数")
    etf_realtime: int = Field(..., description="实时数据记录数")
    etf_history: int = Field(..., description="历史数据记录数")
    screening_results: int = Field(..., description="筛选结果记录数")
    backtest_results: int = Field(..., description="回测结果记录数")
    realtime_date_range: str = Field(..., description="实时数据日期范围")
    history_date_range: str = Field(..., description="历史数据日期范围")
    unique_history_codes: int = Field(..., description="历史数据唯一ETF代码数")


class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
