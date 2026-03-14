"""
历史数据API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import pandas as pd

from data.etf_data_fetcher import ETFDataFetcher
from data.database import DatabaseManager
from indicators.technical_indicators import TechnicalIndicators
from api.models.schemas import HistoryData, IndicatorData, ApiResponse

router = APIRouter(prefix="/api/history", tags=["历史数据"])

fetcher = None
db_manager = None


def init_services():
    """初始化服务"""
    global fetcher, db_manager
    if fetcher is None:
        db_manager = DatabaseManager()
        fetcher = ETFDataFetcher(db_manager=db_manager)


@router.get("/{symbol}", response_model=ApiResponse)
async def get_history(
    symbol: str,
    start_date: Optional[str] = Query(None, description="开始日期(YYYYMMDD)，不指定则返回全部历史数据"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYYMMDD)，不指定则返回至最新")
):
    """
    获取指定ETF的历史数据
    
    - **symbol**: ETF代码
    - **start_date**: 开始日期(YYYYMMDD)，不指定则返回全部历史数据
    - **end_date**: 结束日期(YYYYMMDD)，不指定则返回至最新
    """
    init_services()
    
    try:
        df = fetcher.get_etf_history(symbol, start_date, end_date)
        
        if df.empty:
            return ApiResponse(
                success=False,
                message=f"未找到ETF {symbol} 在 {start_date} ~ {end_date} 的历史数据",
                data=None
            )
        
        data = []
        for _, row in df.iterrows():
            data.append(HistoryData(
                code=symbol,
                date=str(row.get('日期', '')),
                open=float(row.get('开盘', 0)) if pd.notna(row.get('开盘')) else None,
                high=float(row.get('最高', 0)) if pd.notna(row.get('最高')) else None,
                low=float(row.get('最低', 0)) if pd.notna(row.get('最低')) else None,
                close=float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else None,
                volume=float(row.get('成交量', 0)) if pd.notna(row.get('成交量')) else None,
                amount=float(row.get('成交额', 0)) if pd.notna(row.get('成交额')) else None
            ).model_dump())
        
        return ApiResponse(
            success=True,
            message=f"获取到 {len(data)} 条历史数据",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}/indicators", response_model=ApiResponse)
async def get_history_with_indicators(
    symbol: str,
    start_date: str = Query(..., description="开始日期(YYYYMMDD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYYMMDD)"),
    indicators: Optional[str] = Query("all", description="技术指标: all, macd, bb, rsi")
):
    """
    获取历史数据及技术指标
    
    - **symbol**: ETF代码
    - **start_date**: 开始日期(YYYYMMDD)
    - **end_date**: 结束日期(YYYYMMDD)
    - **indicators**: 技术指标类型
    """
    init_services()
    
    try:
        df = fetcher.get_etf_history(symbol, start_date, end_date)
        
        if df.empty:
            return ApiResponse(
                success=False,
                message=f"未找到ETF {symbol} 的历史数据",
                data=None
            )
        
        df = TechnicalIndicators.calculate_all(df)
        
        data = []
        for _, row in df.iterrows():
            indicator_data = IndicatorData(
                date=str(row.get('日期', '')),
                close=float(row.get('收盘', 0)) if pd.notna(row.get('收盘')) else None
            )
            
            if indicators in ['all', 'macd']:
                indicator_data.macd = float(row.get('macd_fast', 0)) if pd.notna(row.get('macd_fast')) else None
                indicator_data.macd_signal = float(row.get('macd_signal', 0)) if pd.notna(row.get('macd_signal')) else None
                indicator_data.macd_hist = float(row.get('macd_hist', 0)) if pd.notna(row.get('macd_hist')) else None
            
            if indicators in ['all', 'bb']:
                indicator_data.bb_upper = float(row.get('bb_upper', 0)) if pd.notna(row.get('bb_upper')) else None
                indicator_data.bb_middle = float(row.get('bb_middle', 0)) if pd.notna(row.get('bb_middle')) else None
                indicator_data.bb_lower = float(row.get('bb_lower', 0)) if pd.notna(row.get('bb_lower')) else None
            
            if indicators in ['all', 'rsi']:
                indicator_data.rsi = float(row.get('rsi', 0)) if pd.notna(row.get('rsi')) else None
            
            data.append(indicator_data.model_dump())
        
        return ApiResponse(
            success=True,
            message=f"获取到 {len(data)} 条历史数据及技术指标",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
