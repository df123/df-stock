"""
筛选API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from screening.stock_screener import ETFScreener
from api.models.schemas import ApiResponse

router = APIRouter(prefix="/api/screening", tags=["筛选"])

screener = None


def init_services():
    """初始化服务"""
    global screener
    if screener is None:
        screener = ETFScreener(min_days=30)


@router.get("/combined", response_model=ApiResponse)
async def screen_combined(
    end_date: Optional[str] = Query(None, description="筛选日期(YYYYMMDD)"),
    period: Optional[str] = Query('daily', description="周期类型(daily/weekly)"),
    lookback_days: Optional[int] = Query(60, description="回溯天数"),
    require_macd_golden: Optional[bool] = Query(True, description="要求MACD金叉"),
    require_bb_above_middle: Optional[bool] = Query(True, description="要求价格在布林带中轨之上"),
    limit: Optional[int] = Query(50, description="筛选ETF数量限制")
):
    """
    MACD+布林带组合策略筛选
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **require_macd_golden**: 是否要求MACD金叉
    - **require_bb_above_middle**: 是否要求价格在布林带中轨之上
    - **limit**: 筛选ETF数量限制
    """
    init_services()
    
    try:
        normalized_end_date = end_date if end_date else None
        
        print(f"[DEBUG] screen_combined called with params:")
        print(f"  end_date: {end_date}")
        print(f"  normalized_end_date: {normalized_end_date}")
        print(f"  lookback_days: {lookback_days}")
        print(f"  require_macd_golden: {require_macd_golden}")
        print(f"  require_bb_above_middle: {require_bb_above_middle}")
        
        df = screener.screen_by_combined(
            end_date=normalized_end_date,
            lookback_days=lookback_days,
            require_macd_golden=require_macd_golden,
            require_bb_above_middle=require_bb_above_middle
        )
        
        print(f"[DEBUG] screen_combined result: {len(df)} rows")
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/macd", response_model=ApiResponse)
async def screen_macd(
    end_date: Optional[str] = Query(None, description="筛选日期(YYYYMMDD)"),
    period: Optional[str] = Query('daily', description="周期类型(daily/weekly)"),
    lookback_days: Optional[int] = Query(60, description="回溯天数"),
    include_golden_cross: Optional[bool] = Query(True, description="包含金叉信号"),
    include_death_cross: Optional[bool] = Query(False, description="包含死叉信号"),
    limit: Optional[int] = Query(50, description="筛选ETF数量限制")
):
    """
    MACD策略筛选
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **include_golden_cross**: 是否包含金叉信号
    - **include_death_cross**: 是否包含死叉信号
    - **limit**: 筛选ETF数量限制
    """
    init_services()
    
    try:
        normalized_end_date = end_date if end_date else None
        
        df = screener.screen_by_macd(
            end_date=normalized_end_date,
            lookback_days=lookback_days,
            include_golden_cross=include_golden_cross,
            include_death_cross=include_death_cross
        )
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bollinger", response_model=ApiResponse)
async def screen_bollinger(
    end_date: Optional[str] = Query(None, description="筛选日期(YYYYMMDD)"),
    period: Optional[str] = Query('daily', description="周期类型(daily/weekly)"),
    lookback_days: Optional[int] = Query(60, description="回溯天数"),
    include_upper_break: Optional[bool] = Query(True, description="包含上轨突破"),
    include_lower_break: Optional[bool] = Query(False, description="包含下轨突破"),
    include_squeeze: Optional[bool] = Query(False, description="包含布林带收窄"),
    limit: Optional[int] = Query(50, description="筛选ETF数量限制")
):
    """
    布林带策略筛选
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **include_upper_break**: 是否包含上轨突破
    - **include_lower_break**: 是否包含下轨突破
    - **include_squeeze**: 是否包含布林带收窄
    - **limit**: 筛选ETF数量限制
    """
    init_services()
    
    try:
        normalized_end_date = end_date if end_date else None
        
        df = screener.screen_by_bollinger(
            end_date=normalized_end_date,
            lookback_days=lookback_days,
            include_upper_break=include_upper_break,
            include_lower_break=include_lower_break,
            include_squeeze=include_squeeze
        )
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/volume", response_model=ApiResponse)
async def screen_volume(
    end_date: Optional[str] = Query(None, description="筛选日期(YYYYMMDD)"),
    period: Optional[str] = Query('daily', description="周期类型(daily/weekly)"),
    lookback_days: Optional[int] = Query(20, description="回溯天数"),
    min_volume_ratio: Optional[float] = Query(2.0, description="最小成交量倍数"),
    limit: Optional[int] = Query(50, description="筛选ETF数量限制")
):
    """
    成交量策略筛选
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **min_volume_ratio**: 最小成交量倍数（相对于平均成交量）
    - **limit**: 筛选ETF数量限制
    """
    init_services()
    
    try:
        normalized_end_date = end_date if end_date else None
        
        df = screener.screen_by_volume(
            min_volume_ratio=min_volume_ratio,
            lookback_days=lookback_days
        )
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
