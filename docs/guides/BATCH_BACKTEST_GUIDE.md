# 批量推演功能使用指南

## 功能概述

批量推演功能允许您对筛选出的ETF，按照当前筛选条件的策略逻辑（如MACD金叉买入、死叉卖出）进行批量回测，并在筛选结果表格中直接查看推演结果。

## 使用方法

### 前端使用

1. **进入策略筛选页面**
   - 访问 http://localhost:8080
   - 点击"策略筛选"菜单

2. **配置筛选条件**
   - 选择策略类型（MACD、布林带、组合策略等）
   - 设置筛选参数（回溯天数、筛选日期等）
   - 勾选"批量推演"开关
   - 选择推演年限（3年、5年、10年）

3. **执行筛选+推演**
   - 点击"筛选+推演"按钮
   - 系统会先筛选符合条件的ETF
   - 然后对每个ETF执行推演（金叉买入、死叉卖出）
   - 推演结果会直接显示在表格中

4. **查看推演结果**
   - **收获金额**：推演的盈亏金额（正数为盈利，负数为亏损）
   - **收益率**：推演的总收益率（百分比）
   - **最大回撤**：推演期间的最大回撤率（红色显示）
   - **胜率**：盈利交易占比（绿色>50%，橙色≤50%）
   - **交易次数**：推演期间的总交易次数

5. **查看统计汇总**
   - 页面顶部会显示推演完成后的统计信息
   - **平均收益率**：所有ETF的平均收益率
   - **盈利ETF数**：盈利的ETF数量/总数量
   - **平均胜率**：所有ETF的平均胜率

### API调用

#### MACD策略批量推演（金叉买入死叉卖出）

```python
import requests

response = requests.get(
    "http://localhost:8000/api/screening/macd",
    params={
        "lookback_days": 60,           # 回溯天数
        "include_golden_cross": True,   # 包含金叉
        "include_death_cross": False,   # 不包含死叉
        "limit": 10,                   # 筛选ETF数量
        "backtest": True,              # 启用批量推演
        "backtest_years": 10            # 推演年限
    }
)

data = response.json()

for item in data['data']:
    print(f"代码: {item['code']}")
    print(f"收获金额: {item['bt_profit']:.2f}")
    print(f"收益率: {item['bt_return_rate'] * 100:.2f}%")
    print(f"最大回撤: {item['bt_max_drawdown'] * 100:.2f}%")
    print(f"胜率: {item['bt_win_rate'] * 100:.2f}%")
```

#### 组合策略批量推演

```python
import requests

response = requests.get(
    "http://localhost:8000/api/screening/combined",
    params={
        "lookback_days": 60,
        "require_macd_golden": True,
        "require_bb_above_middle": True,
        "limit": 5,
        "backtest": True,
        "backtest_years": 10
    }
)

data = response.json()
```

## 推演策略说明

### MACD策略（金叉买入死叉卖出）

**推演逻辑：**
- 当MACD快线上穿慢线（金叉）时买入
- 当MACD快线下穿慢线（死叉）时卖出
- 使用基础MACD策略进行推演

**适用场景：**
- 适合趋势明确的市场
- 适合中长线投资

### 组合策略

**推演逻辑：**
- 当MACD金叉 + 价格在布林带中轨之上时买入
- 当MACD死叉 或 价格低于布林带下轨时卖出
- 使用标准组合策略进行推演

**适用场景：**
- 适合震荡向上市场
- 风险相对较低

## 推演结果解读

| 指标 | 说明 | 理想值 |
|------|------|--------|
| 收获金额 | 推演期间的盈亏金额 | >0（盈利） |
| 收益率 | 收获金额 / 初始资金 * 100% | >10% |
| 最大回撤 | 从峰值到谷底的最大下跌 | <10% |
| 胜率 | 盈利交易占比 | >50% |
| 交易次数 | 推演期间的总交易次数 | 适中（避免过度交易） |

## 性能说明

- **3年推演**：约3-5秒/5个ETF
- **5年推演**：约5-8秒/5个ETF
- **10年推演**：约8-15秒/5个ETF

建议：
- 初次测试使用3年推演，快速了解策略表现
- 深度分析使用10年推演，获得更长期的数据
- 建议限制每次筛选的ETF数量（如10-20个），避免等待时间过长

## 注意事项

1. **数据要求**：推演需要ETF有足够的历史数据，建议选择上市时间较长的ETF
2. **推演时间**：10年推演可能需要较长时间，请耐心等待
3. **结果解读**：推演结果仅供参考，实际投资需考虑更多因素（滑点、冲击成本等）
4. **策略选择**：不同策略在不同市场环境下表现差异较大，建议对比多种策略
5. **风险控制**：推演不考虑风险控制措施（如止损），实际投资应做好风险管理

## 完整示例

### 前端操作示例

1. 选择策略类型：MACD
2. 勾选"批量推演"
3. 选择推演年限：10年
4. 点击"筛选+推演"按钮
5. 等待推演完成（可能需要10-20秒）
6. 查看表格中的推演结果
7. 查看页面顶部的统计汇总

### Python脚本示例

```python
import requests
import time

def batch_backtest_macd(years=10, limit=10):
    """MACD金叉买入死叉卖出批量推演"""
    
    start_time = time.time()
    
    response = requests.get(
        "http://localhost:8000/api/screening/macd",
        params={
            "lookback_days": 60,
            "include_golden_cross": True,
            "include_death_cross": False,
            "limit": limit,
            "backtest": True,
            "backtest_years": years
        }
    )
    
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"筛选+推演完成，耗时: {elapsed_time:.2f}秒")
        print(f"筛选出 {len(data['data'])} 个ETF")
        
        # 统计
        total_profit = 0
        profit_count = 0
        total_win_rate = 0
        win_rate_count = 0
        
        print(f"\n{'代码':<12} {'名称':<20} {'收获金额':<12} {'收益率':<10} {'最大回撤':<10} {'胜率':<10}")
        print("-" * 80)
        
        for item in data['data']:
            profit = item['bt_profit'] or 0
            return_rate = (item['bt_return_rate'] or 0) * 100
            drawdown = (item['bt_max_drawdown'] or 0) * 100
            win_rate = (item['bt_win_rate'] or 0) * 100
            
            total_profit += profit
            if profit > 0:
                profit_count += 1
            if item['bt_win_rate'] is not None:
                total_win_rate += item['bt_win_rate']
                win_rate_count += 1
            
            print(f"{item['code']:<12} {item['name']:<20} "
                  f"{profit:>10.2f}   {return_rate:>7.2f}%   "
                  f"{drawdown:>7.2f}%   {win_rate:>7.2f}%")
        
        # 统计汇总
        avg_profit = total_profit / len(data['data']) if data['data'] else 0
        avg_win_rate = (total_win_rate / win_rate_count) if win_rate_count > 0 else 0
        
        print(f"\n统计汇总:")
        print(f"平均收获金额: {avg_profit:.2f}")
        print(f"盈利ETF数: {profit_count}/{len(data['data'])}")
        print(f"平均胜率: {avg_win_rate * 100:.2f}%")

# 执行推演
batch_backtest_macd(years=10, limit=10)
```

## 常见问题

**Q: 为什么有些ETF的推演结果为空？**
A: 可能是ETF历史数据不足，或上市时间太短，无法进行长期推演。

**Q: 推演时间太长怎么办？**
A: 可以减少推演年限（如从10年改为3年），或减少筛选的ETF数量。

**Q: 如何选择最优的ETF？**
A: 综合考虑收益率、最大回撤、胜率等指标，优先选择收益率高、回撤小、胜率高的ETF。

**Q: 推演结果可以保证未来收益吗？**
A: 不可以。推演基于历史数据，未来市场环境可能发生变化，推演结果仅供参考。

## 测试命令

```bash
# 测试MACD批量推演（3年）
curl "http://localhost:8000/api/screening/macd?lookback_days=60&include_golden_cross=true&limit=5&backtest=true&backtest_years=3"

# 测试组合策略批量推演（5年）
curl "http://localhost:8000/api/screening/combined?lookback_days=60&require_macd_golden=true&require_bb_above_middle=true&limit=3&backtest=true&backtest_years=5"
```

## 文件位置

- 后端路由：`api/routers/screening.py`
- 前端页面：`web/src/views/Screening.vue`
- 使用指南：`docs/guides/BATCH_BACKTEST_GUIDE.md`
