# 策略推演功能快速参考

## 快速开始

### 前端使用（推荐）

1. **启动服务**
   ```bash
   # 后端
   ./scripts/start_api.sh
   
   # 前端
   cd web
   npm run dev
   ```

2. **访问页面**
   - 打开浏览器访问：http://localhost:8080
   - 点击"策略筛选"菜单

3. **执行推演**
   - 在筛选结果中，点击任意ETF行的"策略推演"按钮
   - 选择策略类型（如：组合策略）
   - 选择子类型（如：标准组合）
   - 选择推演年限（推荐10年）
   - 点击"开始推演"
   - 查看实时进度和详细结果

### API调用

```python
import requests
import time

# 1. 创建回测任务
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

# 2. 轮询进度
while True:
    response = requests.get(f"http://localhost:8000/api/backtest/progress/{task_id}")
    data = response.json()['data']
    
    if data['status'] == 'completed':
        result = data['result']
        print(f"收益率: {result['total_return'] * 100:.2f}%")
        print(f"胜率: {result['win_rate'] * 100:.2f}%")
        break
    elif data['status'] == 'failed':
        print(f"失败: {data.get('error')}")
        break
    
    time.sleep(1)
```

## API端点

### 获取策略列表
```
GET /api/backtest/strategies
```

### 创建回测任务
```
POST /api/backtest/run
参数:
  - code: ETF代码（如510300）
  - strategy_type: 策略类型（macd/bollinger/combined）
  - strategy_subtype: 子类型
  - start_date: 开始日期（YYYYMMDD）
  - initial_cash: 初始资金（默认100000）
```

### 查询进度
```
GET /api/backtest/progress/{task_id}
```

## 支持的策略

### MACD策略
- basic: 基础MACD
- enhanced: 增强MACD

### 布林带策略
- breakthrough: 突破策略
- mean_reversion: 均值回归策略
- squeeze: 收缩突破策略

### 组合策略
- standard: 标准组合
- aggressive: 激进组合
- conservative: 保守组合

## 回测结果说明

| 指标 | 说明 | 理想值 |
|------|------|--------|
| 收获金额 | 最终价值 - 初始资金 | >0 |
| 收益率 | 收获金额 / 初始资金 | >10% |
| 最大回撤率 | 从峰值到谷底的最大下跌 | <10% |
| 夏普比率 | 风险调整后的收益率 | >1 |
| 胜率 | 盈利交易占比 | >50% |

## 常见问题

**Q: 回测需要多长时间？**
A: 通常1-10年回测需要3-30秒，取决于策略复杂度和数据量。

**Q: 可以同时运行多个回测吗？**
A: 可以，每个回测都有独立的任务ID。

**Q: 哪个策略最好？**
A: 没有绝对最好的策略，不同市场环境下表现不同。建议对比多个策略。

**Q: 回测结果可靠吗？**
A: 回测仅供参考，实际投资需要考虑更多因素（滑点、冲击成本等）。

**Q: 如何提高胜率？**
A: 可以尝试保守策略或调整参数，但高胜率不一定代表高收益。

## 测试命令

```bash
# 测试策略列表
curl http://localhost:8000/api/backtest/strategies

# 测试回测
curl -X POST "http://localhost:8000/api/backtest/run?code=510300&strategy_type=combined&strategy_subtype=standard&start_date=20140101"

# 查询进度
curl http://localhost:8000/api/backtest/progress/{task_id}
```

## 文件位置

- 后端路由：`api/routers/backtest.py`
- 前端页面：`web/src/views/Screening.vue`
- API定义：`web/src/api/endpoints.js`
- 使用指南：`docs/guides/STRATEGY_BACKTEST_GUIDE.md`
- 实现文档：`docs/implementation/STRATEGY_BACKTEST_IMPLEMENTATION.md`
