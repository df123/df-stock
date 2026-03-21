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
