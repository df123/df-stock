"""
数据库查询API路由
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, List

from data.database import DatabaseManager
from api.models.schemas import DatabaseStats, ApiResponse

router = APIRouter(prefix="/api/db", tags=["数据库"])

db_manager = None
update_task_status = {
    'running': False,
    'message': '',
    'progress': 0
}


def init_services():
    """初始化服务"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()


@router.get("/stats", response_model=ApiResponse)
async def get_db_stats():
    """获取数据库统计信息"""
    init_services()
    
    try:
        stats = db_manager.get_stats()
        
        stats_data = DatabaseStats(**stats)
        
        return ApiResponse(
            success=True,
            message="数据库统计信息",
            data=stats_data.model_dump()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/etf_list", response_model=ApiResponse)
async def get_etf_list(
    code: Optional[str] = Query(None, description="ETF代码"),
    fund_type: Optional[str] = Query(None, description="基金类型")
):
    """
    获取可交易ETF列表
    返回当前正在交易的ETF代码和名称
    
    - **code**: 筛选特定ETF代码
    - **fund_type**: 筛选特定基金类型
    """
    init_services()
    
    try:
        df = db_manager.query_etf_list(code, fund_type)
        
        data = []
        for _, row in df.iterrows():
            data.append({
                'code': str(row.get('code', '')),
                'name': str(row.get('name', '')),
                'fund_type': str(row.get('fund_type', ''))
            })
        
        return ApiResponse(
            success=True,
            message=f"获取到 {len(data)} 个可交易ETF",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/etf_history", response_model=ApiResponse)
async def query_etf_history(
    code: Optional[str] = Query(None, description="ETF代码"),
    start_date: Optional[str] = Query(None, description="开始日期(YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期(YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, description="返回记录数限制")
):
    """
    查询历史数据
    
    - **code**: ETF代码
    - **start_date**: 开始日期(YYYY-MM-DD)
    - **end_date**: 结束日期(YYYY-MM-DD)
    - **limit**: 返回记录数限制
    """
    init_services()
    
    try:
        df = db_manager.query_etf_history(code or '', start_date, end_date)
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"查询到 {len(data)} 条历史数据",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/screening_results", response_model=ApiResponse)
async def query_screening_results(
    strategy: Optional[str] = Query(None, description="策略类型"),
    code: Optional[str] = Query(None, description="ETF代码"),
    screen_date: Optional[str] = Query(None, description="筛选日期(YYYY-MM-DD)"),
    limit: Optional[int] = Query(100, description="返回记录数限制")
):
    """
    查询筛选结果
    
    - **strategy**: 策略类型
    - **code**: ETF代码
    - **screen_date**: 筛选日期(YYYY-MM-DD)
    - **limit**: 返回记录数限制
    """
    init_services()
    
    try:
        df = db_manager.query_screening_results(strategy, code, screen_date)
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"查询到 {len(data)} 条筛选结果",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/query/backtest_results", response_model=ApiResponse)
async def query_backtest_results(
    strategy: Optional[str] = Query(None, description="策略类型"),
    code: Optional[str] = Query(None, description="ETF代码"),
    limit: Optional[int] = Query(100, description="返回记录数限制")
):
    """
    查询回测结果
    
    - **strategy**: 策略类型
    - **code**: ETF代码
    - **limit**: 返回记录数限制
    """
    init_services()
    
    try:
        df = db_manager.query_backtest_results(strategy, code)
        
        if limit:
            df = df.head(limit)
        
        data = df.to_dict('records')
        
        return ApiResponse(
            success=True,
            message=f"查询到 {len(data)} 条回测结果",
            data=data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{table}", response_model=ApiResponse)
async def export_table(table: str):
    """
    导出表数据为CSV
    
    - **table**: 表名 (etf_history, screening_results, backtest_results)
    """
    init_services()
    
    try:
        valid_tables = ['etf_history', 'screening_results', 'backtest_results']
        if table not in valid_tables:
            return ApiResponse(
                success=False,
                message=f"无效的表名，必须是: {', '.join(valid_tables)}",
                data=None
            )
        
        output_path = db_manager.export_to_csv(table)
        
        return ApiResponse(
            success=True,
            message=f"数据已导出到: {output_path}",
            data={"file_path": output_path}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def run_incremental_update(codes: Optional[List[str]] = None):
    """后台运行增量更新任务"""
    import sys
    import os
    
    sys.path.insert(0, '/home/df/df-stock')
    
    from scripts.incremental_update import IncrementalUpdater
    
    global update_task_status
    
    def progress_callback(progress, message, current=None, total=None):
        """进度回调函数"""
        update_task_status['progress'] = progress
        update_task_status['message'] = message
        if current is not None and total is not None:
            update_task_status['current'] = current
            update_task_status['total'] = total
    
    try:
        update_task_status['running'] = True
        update_task_status['message'] = '正在启动增量更新...'
        update_task_status['progress'] = 0
        update_task_status['current'] = 0
        update_task_status['total'] = 0
        
        updater = IncrementalUpdater(progress_callback=progress_callback)
        
        if codes:
            update_task_status['message'] = f'正在更新 {len(codes)} 个ETF...'
        else:
            update_task_status['message'] = '正在更新所有ETF...'
        
        results = updater.update_all(codes=codes, verbose=False)
        
        update_task_status['message'] = f'更新完成: {results["updated_codes"]} 个ETF, 新增 {results["new_records"]} 条记录'
        update_task_status['progress'] = 100
        
    except Exception as e:
        update_task_status['message'] = f'更新失败: {str(e)}'
        update_task_status['progress'] = 0
    finally:
        update_task_status['running'] = False


@router.post("/update/incremental", response_model=ApiResponse)
async def incremental_update(
    background_tasks: BackgroundTasks,
    codes: Optional[List[str]] = Query(None, description="指定要更新的ETF代码列表")
):
    """
    增量更新ETF历史数据（后台任务）
    
    对于每个ETF，从数据库中最新日期的下一天开始获取新数据
    如果没有指定codes，则更新所有ETF
    
    - **codes**: 可选，指定要更新的ETF代码列表
    """
    global update_task_status
    
    if update_task_status['running']:
        return ApiResponse(
            success=False,
            message="已有更新任务正在运行中",
            data=update_task_status
        )
    
    background_tasks.add_task(run_incremental_update, codes)
    
    return ApiResponse(
        success=True,
        message="增量更新任务已启动，请在几分钟后查看状态",
        data=update_task_status
    )


@router.get("/update/status", response_model=ApiResponse)
async def get_update_status():
    """
    获取增量更新任务状态
    """
    global update_task_status
    
    return ApiResponse(
        success=True,
        message="更新任务状态",
        data=update_task_status
    )
