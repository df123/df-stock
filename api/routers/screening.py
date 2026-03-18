"""
筛选API路由
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta

from screening.stock_screener import ETFScreener
from backtest.backtest_engine import BacktestEngine
from data.etf_data_fetcher import ETFDataFetcher
from api.models.schemas import ApiResponse

router = APIRouter(prefix="/api/screening", tags=["筛选"])

screener = None
fetcher = ETFDataFetcher()
engine = BacktestEngine()


def init_services():
    """初始化服务"""
    global screener
    if screener is None:
        screener = ETFScreener(min_days=30)


def run_backtest_for_etf(code: str, strategy_type: str, years: int = 10) -> dict:
    """
    对单个ETF执行回测
    
    Args:
        code: ETF代码
        strategy_type: 策略类型（macd/basic, macd/enhanced, bollinger/breakthrough等）
        years: 回测年限
    
    Returns:
        回测结果字典
    """
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365)
        
        start_date_str = start_date.strftime('%Y%m%d')
        
        df = fetcher.get_etf_history(code, start_date_str)
        
        if df.empty or len(df) < 100:
            return None
        
        strategy_category, strategy_subtype = strategy_type.split('/', 1)
        
        if strategy_category == 'macd':
            results, _ = engine.run_macd_backtest(df, strategy_subtype)
        elif strategy_category == 'bollinger':
            results, _ = engine.run_bb_backtest(df, strategy_subtype)
        elif strategy_category == 'combined':
            results, _ = engine.run_combined_backtest(df, strategy_subtype)
        else:
            return None
        
        return results
    except Exception as e:
        print(f"回测 {code} 失败: {e}")
        return None


@router.get("/combined", response_model=ApiResponse)
async def screen_combined(
    end_date: Optional[str] = Query(None, description="筛选日期(YYYYMMDD)"),
    period: Optional[str] = Query('daily', description="周期类型(daily/weekly)"),
    lookback_days: Optional[int] = Query(60, description="回溯天数"),
    require_macd_golden: Optional[bool] = Query(True, description="要求MACD金叉"),
    require_bb_above_middle: Optional[bool] = Query(True, description="要求价格在布林带中轨之上"),
    limit: Optional[int] = Query(50, description="筛选ETF数量限制"),
    backtest: Optional[bool] = Query(False, description="是否进行批量推演"),
    backtest_years: Optional[int] = Query(10, description="推演年限（默认10年）")
):
    """
    MACD+布林带组合策略筛选
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **require_macd_golden**: 是否要求MACD金叉
    - **require_bb_above_middle**: 是否要求价格在布林带中轨之上
    - **limit**: 筛选ETF数量限制
    - **backtest**: 是否进行批量推演（金叉买入死叉卖出）
    - **backtest_years**: 推演年限，默认10年
    """
    init_services()
    
    try:
        
        print(f"  end_date: {end_date}")
        print(f"  lookback_days: {lookback_days}")
        print(f"  require_macd_golden: {require_macd_golden}")
        print(f"  require_bb_above_middle: {require_bb_above_middle}")
        print(f"  backtest: {backtest}")
        print(f"  backtest_years: {backtest_years}")
        
        df = screener.screen_by_combined(
            end_date=end_date,
            lookback_days=lookback_days,
            require_macd_golden=require_macd_golden,
            require_bb_above_middle=require_bb_above_middle
        )
        
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        # 如果启用批量推演
        if backtest:
            for item in data:
                code = item['code']
                backtest_result = run_backtest_for_etf(code, 'combined/standard', backtest_years)
                
                if backtest_result:
                    item['bt_initial_cash'] = backtest_result['initial_cash']
                    item['bt_final_value'] = backtest_result['final_value']
                    item['bt_profit'] = backtest_result['final_value'] - backtest_result['initial_cash']
                    item['bt_return_rate'] = backtest_result['total_return']
                    item['bt_max_drawdown'] = backtest_result['max_drawdown']
                    item['bt_sharpe_ratio'] = backtest_result['sharpe_ratio']
                    item['bt_win_rate'] = backtest_result['win_rate']
                    item['bt_total_trades'] = backtest_result['total_trades']
                else:
                    item['bt_initial_cash'] = None
                    item['bt_final_value'] = None
                    item['bt_profit'] = None
                    item['bt_return_rate'] = None
                    item['bt_max_drawdown'] = None
                    item['bt_sharpe_ratio'] = None
                    item['bt_win_rate'] = None
                    item['bt_total_trades'] = None
            
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF" + ("（含推演数据）" if backtest else ""),
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
    limit: Optional[int] = Query(50, description="筛选ETF数量限制"),
    backtest: Optional[bool] = Query(False, description="是否进行批量推演"),
    backtest_years: Optional[int] = Query(10, description="推演年限（默认10年）")
):
    """
    MACD策略筛选（金叉买入死叉卖出）
    
    - **period**: daily-日线, weekly-周线
    - **end_date**: 筛选日期(YYYYMMDD)，不填则使用今天
    - **lookback_days**: 历史数据回溯天数
    - **include_golden_cross**: 是否包含金叉信号
    - **include_death_cross**: 是否包含死叉信号
    - **limit**: 筛选ETF数量限制
    - **backtest**: 是否进行批量推演（金叉买入死叉卖出）
    - **backtest_years**: 推演年限，默认10年
    """
    init_services()
    
    try:
        
        df = screener.screen_by_macd(
            end_date=end_date,
            lookback_days=lookback_days,
            include_golden_cross=include_golden_cross,
            include_death_cross=include_death_cross
        )
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        # 如果启用批量推演
        if backtest:
            for item in data:
                code = item['code']
                backtest_result = run_backtest_for_etf(code, 'macd/basic', backtest_years)
                
                if backtest_result:
                    item['bt_initial_cash'] = backtest_result['initial_cash']
                    item['bt_final_value'] = backtest_result['final_value']
                    item['bt_profit'] = backtest_result['final_value'] - backtest_result['initial_cash']
                    item['bt_return_rate'] = backtest_result['total_return']
                    item['bt_max_drawdown'] = backtest_result['max_drawdown']
                    item['bt_sharpe_ratio'] = backtest_result['sharpe_ratio']
                    item['bt_win_rate'] = backtest_result['win_rate']
                    item['bt_total_trades'] = backtest_result['total_trades']
                else:
                    item['bt_initial_cash'] = None
                    item['bt_final_value'] = None
                    item['bt_profit'] = None
                    item['bt_return_rate'] = None
                    item['bt_max_drawdown'] = None
                    item['bt_sharpe_ratio'] = None
                    item['bt_win_rate'] = None
                    item['bt_total_trades'] = None
            
        
        return ApiResponse(
            success=True,
            message=f"筛选到 {len(data)} 个符合条件的ETF" + ("（含推演数据）" if backtest else ""),
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
        
        df = screener.screen_by_bollinger(
            end_date=end_date,
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
