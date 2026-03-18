"""
回测API路由
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional
import asyncio

from backtest.backtest_engine import BacktestEngine
from data.etf_data_fetcher import ETFDataFetcher
from api.models.schemas import ApiResponse

router = APIRouter(prefix="/api/backtest", tags=["回测"])

fetcher = ETFDataFetcher()
engine = BacktestEngine()

progress_store = {}


def init_services():
    """初始化服务"""
    pass


def run_backtest_with_progress(
    task_id: str,
    code: str,
    strategy_type: str,
    strategy_subtype: str,
    start_date: str,
    end_date: str,
    initial_cash: float = 100000,
    commission: float = 0.0003
):
    """
    带进度回调的回测执行
    """
    try:
        progress_store[task_id] = {
            'status': 'running',
            'progress': 0,
            'message': '正在获取数据...',
            'result': None,
            'error': None
        }
        
        progress_store[task_id]['progress'] = 10
        progress_store[task_id]['message'] = '正在获取历史数据...'
        
        df = fetcher.get_etf_history(code, start_date, end_date)
        
        if df.empty:
            progress_store[task_id]['status'] = 'failed'
            progress_store[task_id]['error'] = f'未找到ETF {code} 的历史数据'
            return
        
        progress_store[task_id]['progress'] = 30
        progress_store[task_id]['message'] = '正在执行回测...'
        
        if strategy_type == 'macd':
            results, _ = engine.run_macd_backtest(df, strategy_subtype)
        elif strategy_type == 'bollinger':
            results, _ = engine.run_bb_backtest(df, strategy_subtype)
        elif strategy_type == 'combined':
            results, _ = engine.run_combined_backtest(df, strategy_subtype)
        else:
            progress_store[task_id]['status'] = 'failed'
            progress_store[task_id]['error'] = f'不支持的策略类型: {strategy_type}'
            return
        
        progress_store[task_id]['progress'] = 100
        progress_store[task_id]['message'] = '回测完成'
        progress_store[task_id]['result'] = results
        progress_store[task_id]['status'] = 'completed'
        
    except Exception as e:
        progress_store[task_id]['status'] = 'failed'
        progress_store[task_id]['error'] = str(e)


@router.post("/run", response_model=ApiResponse)
async def run_backtest(
    code: str = Query(..., description="ETF代码"),
    strategy_type: str = Query(..., description="策略类型(macd/bollinger/combined)"),
    strategy_subtype: str = Query('basic', description="策略子类型"),
    start_date: str = Query(..., description="开始日期(YYYYMMDD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYYMMDD)"),
    initial_cash: Optional[float] = Query(100000, description="初始资金"),
    commission: Optional[float] = Query(0.0003, description="手续费率"),
    background_tasks: BackgroundTasks = None
):
    """
    执行策略回测
    
    - **code**: ETF代码（如510300）
    - **strategy_type**: 策略类型（macd/bollinger/combined）
    - **strategy_subtype**: 策略子类型
      - macd: basic/enhanced
      - bollinger: breakthrough/mean_reversion/squeeze
      - combined: standard/aggressive/conservative
    - **start_date**: 开始日期(YYYYMMDD)
    - **end_date**: 结束日期(YYYYMMDD)，不填则使用今天
    - **initial_cash**: 初始资金，默认100000
    - **commission**: 手续费率，默认0.0003
    
    返回任务ID，可用于查询进度
    """
    init_services()
    
    try:
        import uuid
        task_id = str(uuid.uuid4())
        
        normalized_end_date = end_date if end_date else None
        
        background_tasks.add_task(
            run_backtest_with_progress,
            task_id,
            code,
            strategy_type,
            strategy_subtype,
            start_date,
            normalized_end_date,
            initial_cash,
            commission
        )
        
        return ApiResponse(
            success=True,
            message=f"回测任务已创建",
            data={
                'task_id': task_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{task_id}", response_model=ApiResponse)
async def get_progress(task_id: str):
    """
    查询回测进度
    
    - **task_id**: 任务ID
    """
    init_services()
    
    try:
        if task_id not in progress_store:
            return ApiResponse(
                success=False,
                message="任务不存在",
                data=None
            )
        
        progress_data = progress_store[task_id]
        
        response_data = {
            'status': progress_data['status'],
            'progress': progress_data['progress'],
            'message': progress_data['message']
        }
        
        if progress_data['status'] == 'completed':
            response_data['result'] = progress_data['result']
        elif progress_data['status'] == 'failed':
            response_data['error'] = progress_data['error']
        
        return ApiResponse(
            success=True,
            message="查询成功",
            data=response_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategies", response_model=ApiResponse)
async def get_strategies():
    """
    获取可用策略列表
    """
    try:
        strategies = {
            'macd': {
                'name': 'MACD策略',
                'subtypes': {
                    'basic': '基础MACD',
                    'enhanced': '增强MACD'
                }
            },
            'bollinger': {
                'name': '布林带策略',
                'subtypes': {
                    'breakthrough': '突破策略',
                    'mean_reversion': '均值回归策略',
                    'squeeze': '收缩突破策略'
                }
            },
            'combined': {
                'name': '组合策略',
                'subtypes': {
                    'standard': '标准组合',
                    'aggressive': '激进组合',
                    'conservative': '保守组合'
                }
            }
        }
        
        return ApiResponse(
            success=True,
            message="获取策略列表成功",
            data=strategies
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
