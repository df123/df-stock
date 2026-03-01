"""
实时行情API路由
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
import pandas as pd
from datetime import datetime

from data.etf_data_fetcher import ETFDataFetcher
from data.database import DatabaseManager
from api.models.schemas import RealtimeData, ApiResponse

router = APIRouter(prefix="/api/realtime", tags=["实时行情"])

# 全局数据获取器
fetcher = None
db_manager = None


def init_services():
    """初始化服务"""
    global fetcher, db_manager
    if fetcher is None:
        db_manager = DatabaseManager()
        fetcher = ETFDataFetcher(db_manager=db_manager)


@router.get("", response_model=ApiResponse)
async def get_all_realtime(limit: Optional[int] = None):
    """
    获取所有ETF实时行情
    
    - **limit**: 返回记录数限制
    """
    init_services()
    
    try:
        df = fetcher.get_etf_realtime()
        
        if limit:
            df = df.head(limit)
        
        data = []
        for _, row in df.iterrows():
            data.append(RealtimeData(
                code=str(row.get('代码', '')),
                name=str(row.get('名称', '')),
                price=float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                change_percent=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                change_amount=float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
                data_date=str(row.get('数据日期', ''))
            ).model_dump())
        
        return ApiResponse(
            success=True,
            message=f"获取到 {len(data)} 条实时行情数据",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{symbol}", response_model=ApiResponse)
async def get_realtime_by_symbol(symbol: str):
    """
    获取指定ETF的实时行情
    
    - **symbol**: ETF代码
    """
    init_services()
    
    try:
        df = fetcher.get_etf_realtime(symbol)
        
        if df.empty:
            return ApiResponse(
                success=False,
                message=f"未找到ETF代码 {symbol} 的实时数据",
                data=None
            )
        
        row = df.iloc[0]
        data = RealtimeData(
            code=str(row.get('代码', '')),
            name=str(row.get('名称', '')),
            price=float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
            change_percent=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
            change_amount=float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
            data_date=str(row.get('数据日期', ''))
        ).model_dump()
        
        return ApiResponse(
            success=True,
            message=f"获取到ETF {symbol} 的实时行情",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top/gainers", response_model=ApiResponse)
async def get_top_gainers(limit: int = 10):
    """
    获取涨幅前N名的ETF
    
    - **limit**: 返回记录数
    """
    init_services()
    
    try:
        df = fetcher.get_top_gainers(limit)
        
        data = []
        for _, row in df.iterrows():
            data.append(RealtimeData(
                code=str(row.get('代码', '')),
                name=str(row.get('名称', '')),
                price=float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                change_percent=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                change_amount=float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
                data_date=str(row.get('数据日期', ''))
            ).model_dump())
        
        return ApiResponse(
            success=True,
            message=f"涨幅前{limit}名",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top/losers", response_model=ApiResponse)
async def get_top_losers(limit: int = 10):
    """
    获取跌幅前N名的ETF
    
    - **limit**: 返回记录数
    """
    init_services()
    
    try:
        df = fetcher.get_top_losers(limit)
        
        data = []
        for _, row in df.iterrows():
            data.append(RealtimeData(
                code=str(row.get('代码', '')),
                name=str(row.get('名称', '')),
                price=float(row.get('最新价', 0)) if pd.notna(row.get('最新价')) else None,
                change_percent=float(row.get('涨跌幅', 0)) if pd.notna(row.get('涨跌幅')) else None,
                change_amount=float(row.get('涨跌额', 0)) if pd.notna(row.get('涨跌额')) else None,
                data_date=str(row.get('数据日期', ''))
            ).model_dump())
        
        return ApiResponse(
            success=True,
            message=f"跌幅前{limit}名",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=ApiResponse)
async def search_etf(keyword: str, limit: Optional[int] = 20):
    """
    搜索ETF
    
    - **keyword**: 搜索关键词（ETF名称或代码）
    - **limit**: 返回记录数限制
    """
    init_services()
    
    try:
        df = fetcher.search_etf(keyword)
        
        if limit:
            df = df.head(limit)
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'code': str(row.get('代码', '')),
                'name': str(row.get('名称', '')),
                'fund_type': str(row.get('基金类型', ''))
            })
        
        return ApiResponse(
            success=True,
            message=f"搜索到 {len(data)} 个ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
