# ETF量化分析系统 - 实现总结

## 项目概述

本项目是一个基于AKShare的ETF量化分析系统，实现了完整的ETF数据获取、技术指标计算、策略分析、筛选和回测功能。系统使用Python编写，采用模块化设计，易于扩展和维护。

## 已实现功能

### 1. 数据获取模块 (data/etf_data_fetcher.py)

- ✓ 获取所有ETF列表
- ✓ 获取ETF实时行情数据
- ✓ 获取ETF历史数据（日线、周线、月线）
- ✓ 支持价格调整（前复权、后复权、不复权）
- ✓ 按关键词搜索ETF
- ✓ 获取涨幅/跌幅前N名

### 2. 技术指标模块 (indicators/technical_indicators.py)

- ✓ MACD指标（快线、慢线、信号线、柱状图）
- ✓ 布林带指标（上轨、中轨、下轨、带宽）
- ✓ 移动平均线（SMA）
- ✓ 指数移动平均线（EMA）
- ✓ RSI相对强弱指标
- ✓ 交易信号生成（金叉、死叉、突破等）
- ✓ 所有指标一键计算

### 3. 策略模块

#### MACD策略 (strategies/macd_strategy.py)
- ✓ 基础MACD金叉/死叉策略
- ✓ 增强版MACD策略（支持MACD零轴确认、成交量确认）

#### 布林带策略 (strategies/bollinger_strategy.py)
- ✓ 布林带突破策略
- ✓ 布林带均值回归策略
- ✓ 布林带收缩策略

#### 组合策略 (strategies/combined_strategy.py)
- ✓ 标准组合策略（MACD + 布林带）
- ✓ 激进组合策略（包含布林带收缩）
- ✓ 保守组合策略（包含RSI过滤、趋势确认）

### 4. 回测引擎 (backtest/backtest_engine.py)

- ✓ 统一的数据准备和预处理
- ✓ 策略回测框架
- ✓ 多策略对比功能
- ✓ 回测分析指标：
  - 总收益率
  - 夏普比率
  - 最大回撤
  - 胜率
  - 交易次数

### 5. ETF筛选模块 (screening/stock_screener.py)

- ✓ MACD金叉/死叉筛选
- ✓ 布林带突破筛选
- ✓ 组合策略筛选
- ✓ 放量筛选
- ✓ 批量处理ETF
- ✓ 自定义参数

### 6. 工具模块 (utils/helpers.py)

- ✓ 可视化工具：
  - 价格+技术指标图表
  - MACD信号图表
  - 布林带图表
- ✓ 回测结果格式化
- ✓ 日期工具函数

### 7. 主程序 (main.py)

- ✓ 完整的CLI命令行接口
- ✓ 实时行情查询
- ✓ 历史数据查询
- ✓ 技术指标分析
- ✓ ETF筛选
- ✓ 策略回测
- ✓ 策略对比
- ✓ 图表绘制
- ✓ 结果保存

## 技术栈

- **数据源**: AKShare
- **数据处理**: Pandas, NumPy
- **技术指标**: pandas_ta
- **回测框架**: Backtrader
- **可视化**: Matplotlib
- **编程语言**: Python 3.9+

## 项目结构

```
df-stock/
├── .gitignore                    # Git忽略文件
├── README.md                     # 项目说明文档
├── requirements.txt              # 依赖包列表
├── config.py                     # 配置文件
├── install.sh                    # 安装脚本
├── main.py                       # 主程序入口（CLI）
├── test_system.py                # 系统测试脚本
├── examples.py                   # 使用示例
├── data/                         # 数据获取模块
│   ├── __init__.py
│   └── etf_data_fetcher.py
├── indicators/                   # 技术指标模块
│   ├── __init__.py
│   └── technical_indicators.py
├── strategies/                   # 策略模块
│   ├── __init__.py
│   ├── macd_strategy.py
│   ├── bollinger_strategy.py
│   └── combined_strategy.py
├── backtest/                     # 回测模块
│   ├── __init__.py
│   └── backtest_engine.py
├── screening/                    # 筛选模块
│   ├── __init__.py
│   └── stock_screener.py
└── utils/                        # 工具模块
    ├── __init__.py
    └── helpers.py
```

## 使用方法

### 快速开始

```bash
# 1. 安装依赖
bash install.sh

# 2. 运行测试
python test_system.py

# 3. 查看示例
python examples.py
```

### CLI命令示例

```bash
# 实时行情
python main.py --action realtime --symbol 510300

# 历史数据 + 技术指标
python main.py --action indicators --symbol 510300 --start 20230101 --plot

# ETF筛选
python main.py --action screen --strategy macd

# 策略回测
python main.py --action backtest --strategy macd --symbol 510300 --start 20230101

# 策略对比
python main.py --action backtest --strategy compare --symbol 510300 --start 20230101
```

## 代码特点

1. **模块化设计**: 各功能模块独立，易于维护和扩展
2. **代码复用**: 技术指标、策略等可在多处复用
3. **参数灵活**: 支持自定义各种策略参数
4. **错误处理**: 完善的异常处理机制
5. **代码注释**: 清晰的中文注释说明
6. **类型提示**: 使用Python类型提示提高代码可读性
7. **测试脚本**: 提供完整的测试脚本验证功能

## 支持的策略

### MACD策略
- 基础: MACD快慢线交叉
- 增强: 增加MACD零轴确认、成交量确认

### 布林带策略
- 突破: 价格突破上下轨
- 均值回归: 价格偏离均值后的回归
- 收缩: 布林带收缩后的趋势启动

### 组合策略
- 标准: MACD金叉 + 价格在中轨上方
- 激进: 布林带收缩 + MACD金叉 + 趋势确认
- 保守: MACD金叉 + 趋势确认 + RSI过滤 + 价格在中轨上方

## 回测指标

- 初始资金
- 最终资金
- 总收益率
- 夏普比率
- 最大回撤
- 最大回撤金额
- 总交易次数
- 获胜次数
- 失败次数
- 胜率

## 筛选功能

- MACD金叉/死叉信号
- 布林带上轨/下轨突破
- 组合策略信号
- 成交量异常放大

## 可视化功能

- 价格走势 + 移动平均线 + 布林带
- MACD指标 + 买卖信号
- 布林带 + 价格位置
- RSI指标 + 超买超卖区域
- 支持保存为图片文件

## 扩展方向

1. 添加更多技术指标（KDJ、CCI、ATR等）
2. 实现更多策略类型（均线策略、趋势策略等）
3. 添加风险控制模块（止损、止盈）
4. 实现实时监控和报警
5. 添加Web界面
6. 支持更多数据源
7. 添加机器学习模型

## 注意事项

1. 数据来源为公开渠道，请自行验证数据准确性
2. 策略回测结果不代表未来表现
3. 实际交易需考虑滑点、手续费等成本
4. 本系统仅供学习研究使用，不构成投资建议
5. 请根据自身风险承受能力合理投资

## 许可证

MIT License
