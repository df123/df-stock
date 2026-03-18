# 功能分离说明

## 功能概述

根据用户需求，将原来的策略推演功能拆分为两个独立的页面：

1. **策略筛选页面** (`/screening`) - ETF筛选 + 批量推演
2. **策略推演页面** (`/backtest`) - 单个ETF详细推演

## 页面1：策略筛选 (`/screening`)

### 功能说明

- **筛选ETF**：按照MACD、布林带、组合策略等条件筛选ETF
- **批量推演**：对筛选出的所有ETF执行批量推演（金叉买入、死叉卖出）
- **推演结果展示**：在表格中直接显示每个ETF的推演结果

### 主要特性

1. **筛选功能**
   - 支持多种策略类型（MACD、布林带、组合策略）
   - 可配置筛选参数（回溯天数、筛选日期等）
   - 点击"筛选"按钮执行筛选

2. **批量推演功能**
   - 勾选"批量推演"区域
   - 选择推演年限（3年、5年、10年）
   - 点击"批量推演"按钮执行
   - 实时显示推演进度

3. **结果展示**
   - 表格新增推演结果列：
     - 收获金额
     - 收益率（绿色盈利/红色亏损）
     - 最大回撤（红色显示）
     - 胜率（绿色>50%）
     - 交易次数
   - 顶部显示统计汇总：
     - 平均收益率
     - 盈利ETF数
     - 平均胜率

### 使用流程

1. 选择策略类型（如：MACD）
2. 设置筛选参数（回溯天数等）
3. 点击"筛选"按钮
4. 查看筛选结果
5. 勾选"批量推演"，选择推演年限
6. 点击"批量推演"按钮
7. 查看每个ETF的推演结果

### API调用

```python
import requests

# 筛选 + 批量推演
response = requests.get(
    "http://localhost:8000/api/screening/macd",
    params={
        "lookback_days": 60,
        "include_golden_cross": True,
        "include_death_cross": False,
        "limit": 10,
        "backtest": True,
        "backtest_years": 10
    }
)

data = response.json()

for item in data['data']:
    print(f"{item['code']}: {item['bt_profit']:.2f} ({item['bt_return_rate'] * 100:.2f}%)")
```

## 页面2：策略推演 (`/backtest`)

### 功能说明

- **单个ETF推演**：对指定ETF执行详细的策略推演
- **实时进度**：显示推演进度和状态
- **详细结果**：展示完整的回测结果
- **策略说明**：显示当前推演策略的详细说明

### 主要特性

1. **推演配置**
   - 输入ETF代码（如510300）
   - 选择策略类型（MACD、布林带、组合策略）
   - 选择策略子类型
   - 选择推演年限（1年、3年、5年、10年）
   - 设置初始资金

2. **实时进度**
   - 显示推演进度百分比
   - 显示当前状态消息
   - 推演成功/失败提示

3. **详细结果**
   - 初始资金、最终价值
   - 收获金额（颜色标识）
   - 总收益率（百分比）
   - 最大回撤率/金额
   - 夏普比率
   - 交易统计（总次数、盈利/亏损次数、胜率）
   - 策略评级（优秀/良好/及格/一般/较差）

4. **策略说明**
   - 显示当前推演策略的详细说明
   - 包含买卖规则描述

### 使用流程

1. 输入ETF代码（如510300）
2. 选择策略类型（如：组合策略）
3. 选择策略子类型（如：标准组合）
4. 选择推演年限（如：10年）
5. 设置初始资金（如：100000）
6. 点击"开始推演"按钮
7. 查看实时进度
8. 查看详细结果和策略评级

### API调用

```python
import requests
import time

# 创建推演任务
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
    
    print(f"进度: {progress['progress']}% - {progress['message']}")
    
    if progress['status'] == 'completed':
        result = progress['result']
        print(f"收益率: {result['total_return'] * 100:.2f}%")
        print(f"胜率: {result['win_rate'] * 100:.2f}%")
        break
    elif progress['status'] == 'failed':
        print(f"推演失败: {progress.get('error')}")
        break
    
    time.sleep(1)
```

## 两个页面的区别

| 特性 | 策略筛选页面 | 策略推演页面 |
|------|-------------|-------------|
| 主要功能 | 筛选ETF + 批量推演 | 单个ETF详细推演 |
| 推演对象 | 筛选出的所有ETF（批量） | 指定的单个ETF |
| 推演策略 | 固定策略（MACD或组合） | 可选择任意策略 |
| 推演配置 | 年限选择 | 完整配置（代码、策略、年限、资金） |
| 结果展示 | 表格对比 | 详细卡片 + 评级 |
| 适用场景 | 快速对比多个ETF | 深度分析单个ETF |

## 路由配置

```javascript
// web/src/router/index.js
const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/screening',
    name: 'Screening',
    component: () => import('../views/Screening.vue')
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: () => import('../views/Backtest.vue')
  }
  // ... 其他路由
]
```

## 导航菜单

```html
<!-- web/src/App.vue -->
<nav>
  <router-link to="/">仪表盘</router-link>
  <router-link to="/realtime">实时行情</router-link>
  <router-link to="/history">历史数据</router-link>
  <router-link to="/screening">策略筛选</router-link>
  <router-link to="/backtest">策略推演</router-link>
  <router-link to="/database">数据库</router-link>
</nav>
```

## 文件结构

```
web/src/
├── views/
│   ├── Screening.vue      # 策略筛选页面（批量推演）
│   └── Backtest.vue       # 策略推演页面（单个ETF）
├── router/
│   └── index.js          # 路由配置
└── App.vue              # 导航菜单
```

## 测试命令

```bash
# 测试策略筛选页面（批量推演）
curl "http://localhost:8000/api/screening/macd?lookback_days=60&include_golden_cross=true&limit=3&backtest=true&backtest_years=3"

# 测试策略推演页面（单个ETF）
curl -X POST "http://localhost:8000/api/backtest/run?code=510300&strategy_type=combined&strategy_subtype=standard&start_date=20140101&initial_cash=100000"
```

## 使用建议

### 使用策略筛选页面

- **适用场景**：快速对比多个ETF的策略表现
- **推荐流程**：
  1. 筛选出符合条件的ETF
  2. 执行批量推演（3-5年）
  3. 对比各个ETF的收益率和胜率
  4. 选择表现最佳的ETF进行进一步分析

### 使用策略推演页面

- **适用场景**：深度分析单个ETF的历史表现
- **推荐流程**：
  1. 选择感兴趣的ETF
  2. 选择多种策略进行对比测试
  3. 选择10年推演获得更长期的数据
  4. 查看详细的推演结果和策略评级
  5. 评估策略的有效性和适用性

## 总结

通过功能分离，实现了：
- ✅ 更清晰的功能划分
- ✅ 更好的用户体验
- ✅ 更灵活的推演方式
- ✅ 更完整的结果展示
- ✅ 更高效的工作流程
