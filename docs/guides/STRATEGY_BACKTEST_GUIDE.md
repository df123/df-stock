# 策略推演功能使用指南

## 功能概述

策略推演功能允许用户基于历史数据对选定策略进行回测，查看策略在过去10年内的表现，包括：
- 收获金额（最终价值 - 初始资金）
- 总收益率
- 最大回撤率
- 夏普比率
- 交易次数和胜率

## 后端API

### 1. 获取策略列表

```bash
GET /api/backtest/strategies
```

响应示例：
```json
{
  "success": true,
  "message": "获取策略列表成功",
  "data": {
    "macd": {
      "name": "MACD策略",
      "subtypes": {
        "basic": "基础MACD",
        "enhanced": "增强MACD"
      }
    },
    "bollinger": {
      "name": "布林带策略",
      "subtypes": {
        "breakthrough": "突破策略",
        "mean_reversion": "均值回归策略",
        "squeeze": "收缩突破策略"
      }
    },
    "combined": {
      "name": "组合策略",
      "subtypes": {
        "standard": "标准组合",
        "aggressive": "激进组合",
        "conservative": "保守组合"
      }
    }
  }
}
```

### 2. 创建回测任务

```bash
POST /api/backtest/run
```

参数：
- `code`: ETF代码（必填）
- `strategy_type`: 策略类型（必填）：macd/bollinger/combined
- `strategy_subtype`: 策略子类型（必填）
- `start_date`: 开始日期 YYYYMMDD（必填）
- `end_date`: 结束日期 YYYYMMDD（可选，默认为今天）
- `initial_cash`: 初始资金（可选，默认100000）
- `commission`: 手续费率（可选，默认0.0003）

示例：
```bash
curl -X POST "http://localhost:8000/api/backtest/run?code=510300&strategy_type=combined&strategy_subtype=standard&start_date=20140101&initial_cash=100000"
```

响应示例：
```json
{
  "success": true,
  "message": "回测任务已创建",
  "data": {
    "task_id": "ad42e773-82df-4f9f-9ca5-d898bca024e7"
  }
}
```

### 3. 查询回测进度

```bash
GET /api/backtest/progress/{task_id}
```

响应示例：
```json
{
  "success": true,
  "message": "查询成功",
  "data": {
    "status": "completed",
    "progress": 100,
    "message": "回测完成",
    "result": {
      "initial_cash": 100000,
      "final_value": 100001.51,
      "total_return": 0.000015,
      "sharpe_ratio": -2403.98,
      "max_drawdown": 0.00114,
      "max_drawdown_money": 1.14,
      "total_trades": 45,
      "won_trades": 18,
      "lost_trades": 27,
      "win_rate": 0.4
    }
  }
}
```

进度状态：
- `running`: 任务运行中
- `completed`: 任务完成
- `failed`: 任务失败

## 前端使用

### 在筛选页面使用策略推演

1. 进入策略筛选页面
2. 点击任意ETF行的"策略推演"按钮
3. 在弹出的对话框中配置参数：
   - 策略类型：选择MACD、布林带或组合策略
   - 策略子类型：根据策略类型选择具体的子策略
   - 推演年限：选择1年、3年、5年或10年
   - 初始资金：设置初始投资金额（默认100000）
4. 点击"开始推演"按钮
5. 查看实时进度条
6. 推演完成后查看详细结果

### 结果说明

回测结果包含以下指标：

| 指标 | 说明 |
|------|------|
| 初始资金 | 回测开始时的资金 |
| 最终价值 | 回测结束时的账户价值 |
| 收获金额 | 最终价值 - 初始资金（正数为盈利，负数为亏损） |
| 总收益率 | (最终价值 - 初始资金) / 初始资金 * 100% |
| 最大回撤率 | 从峰值到谷底的最大下跌百分比 |
| 最大回撤金额 | 从峰值到谷底的最大下跌金额 |
| 夏普比率 | 风险调整后的收益率，>1为优秀 |
| 交易总次数 | 总共执行的交易次数 |
| 盈利次数 | 盈利的交易次数 |
| 亏损次数 | 亏损的交易次数 |
| 胜率 | 盈利次数 / 交易总次数 * 100% |

## 策略说明

### MACD策略

**基础MACD (basic)**
- MACD快线上穿信号线且MACD > 0时买入
- MACD快线下穿信号线时卖出

**增强MACD (enhanced)**
- 基础MACD条件
- 可选成交量确认

### 布林带策略

**突破策略 (breakthrough)**
- 价格突破布林带上轨时买入
- 价格跌破布林带下轨或达到止盈/止损时卖出

**均值回归策略 (mean_reversion)**
- 价格触及布林带下轨附近时买入
- 价格触及布林带上轨附近时卖出

**收缩突破策略 (squeeze)**
- 布林带收缩时，价格向上突破中轨且高于趋势线时买入
- 价格低于趋势线时卖出

### 组合策略

**标准组合 (standard)**
- MACD金叉 + 价格在布林带中轨之上时买入
- MACD死叉或价格低于布林带下轨时卖出

**激进组合 (aggressive)**
- 布林带收缩 + MACD金叉 + 价格高于趋势线时买入
- MACD死叉时卖出

**保守组合 (conservative)**
- MACD金叉 + MACD > 0 + 均线多头排列 + 价格高于20日均线 + RSI在30-70之间时买入
- MACD死叉或均线空头排列或RSI > 75时卖出

## 技术实现

### 后端实现

- **路由文件**: `api/routers/backtest.py`
- **回测引擎**: `backtest/backtest_engine.py`
- **进度跟踪**: 使用全局字典存储任务进度
- **后台任务**: 使用FastAPI的BackgroundTasks异步执行回测

### 前端实现

- **API端点**: `web/src/api/endpoints.js` 中的 `backtestAPI`
- **页面组件**: `web/src/views/Screening.vue`
- **进度轮询**: 每秒查询一次任务进度，直到完成或失败
- **结果展示**: 使用Element Plus的Descriptions组件展示回测结果

## 注意事项

1. 回测需要足够的历史数据，建议选择上市时间较长的ETF
2. 10年回测可能需要较长时间（取决于数据量）
3. 回测结果仅供参考，实际投资需考虑市场环境变化
4. 手续费设置会影响回测结果，默认为0.03%
5. 不同策略在不同市场环境下表现差异较大

## 测试示例

```python
import requests
import time

# 创建回测任务
response = requests.post(
    "http://localhost:8000/api/backtest/run",
    params={
        "code": "510300",
        "strategy_type": "combined",
        "strategy_subtype": "standard",
        "start_date": "20140101",
        "initial_cash": 100000
    }
)

task_id = response.json()['data']['task_id']

# 轮询进度
while True:
    response = requests.get(f"http://localhost:8000/api/backtest/progress/{task_id}")
    progress = response.json()['data']
    
    if progress['status'] == 'completed':
        result = progress['result']
        print(f"收益率: {result['total_return'] * 100:.2f}%")
        print(f"胜率: {result['win_rate'] * 100:.2f}%")
        break
    elif progress['status'] == 'failed':
        print(f"回测失败: {progress.get('error')}")
        break
    
    time.sleep(1)
```
