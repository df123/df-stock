# ETF量化分析系统

基于AKShare的ETF数据获取与技术分析系统，支持MACD、布林带等多种技术指标策略的分析、筛选和回测。

## 功能特性

- **数据获取**: 使用新浪财经和同花顺获取ETF净值数据和历史行情
- **技术指标**: MACD、布林带、RSI、SMA、EMA等
- **策略分析**: MACD金叉/死叉、布林带突破、组合策略
- **ETF筛选**: 根据策略信号批量筛选ETF
- **回测引擎**: 基于Backtrader的策略回测
- **可视化**: 技术指标图表、策略信号标注

## 数据源说明

| 功能 | 数据源 | 说明 |
|------|--------|------|
| 实时净值行情 | 同花顺 | 基金净值数据，每日更新 |
| ETF列表 | 新浪财经 | 1400+ ETF |
| 历史行情 | 新浪财经 | 支持前复权、后复权 |
| 分红信息 | 新浪财经 | ETF分红历史 |

**注意**: 系统已切换至新浪财经和同花顺数据源，**不再使用东方财富(东财)**

## 快速开始

### 1. 安装依赖

```bash
# 方法1: 使用安装脚本（推荐）
bash install.sh

# 方法2: 手动安装
pip install -r requirements.txt
```

### 2. 运行测试

```bash
# 测试系统功能是否正常
python test_system.py

# 运行示例程序
python examples.py
```

### 3. 开始使用

```bash
# 查看帮助信息
python main.py --help

# 获取实时行情
python main.py --action realtime --symbol 510300

# 技术指标分析
python main.py --action indicators --symbol 510300 --start 20230101

# 策略回测
python main.py --action backtest --strategy macd --symbol 510300 --start 20230101
```

## 项目结构

```
.
├── data/
│   └── etf_data_fetcher.py    # AKShare数据获取
├── indicators/
│   └── technical_indicators.py  # 技术指标计算
├── strategies/
│   ├── macd_strategy.py       # MACD策略
│   ├── bollinger_strategy.py  # 布林带策略
│   └── combined_strategy.py   # 组合策略
├── backtest/
│   └── backtest_engine.py     # 回测引擎
├── screening/
│   └── stock_screener.py      # ETF筛选
├── utils/
│   └── helpers.py             # 工具函数
└── main.py                    # 主程序入口
```

## 使用方法

### 1. 实时行情查询

```bash
# 查询所有ETF实时行情
python main.py --action realtime

# 查询特定ETF实时行情
python main.py --action realtime --symbol 510300

# 查询涨幅/跌幅前10名
python main.py --action realtime --top 10
```

### 2. 历史数据查询

```bash
# 查询历史数据
python main.py --action history --symbol 510300 --start 20230101

# 带技术指标
python main.py --action history --symbol 510300 --start 20230101 --indicators

# 保存到文件
python main.py --action history --symbol 510300 --start 20230101 --save
```

### 3. 技术指标分析

```bash
# 基础技术指标
python main.py --action indicators --symbol 510300 --start 20230101

# 绘制图表
python main.py --action indicators --symbol 510300 --start 20230101 --plot

# 特定指标图表
python main.py --action indicators --symbol 510300 --start 20230101 --plot --indicator macd
python main.py --action indicators --symbol 510300 --start 20230101 --plot --indicator bb
```

### 4. ETF筛选

```bash
# MACD金叉筛选
python main.py --action screen --strategy macd

# 布林带突破筛选
python main.py --action screen --strategy bb

# 组合策略筛选
python main.py --action screen --strategy combined

# 放量筛选
python main.py --action screen --strategy volume --volume-ratio 2.5

# 保存筛选结果
python main.py --action screen --strategy macd --save
```

### 5. 策略回测

```bash
# MACD策略回测
python main.py --action backtest --strategy macd --symbol 510300 --start 20220101

# 布林带策略回测
python main.py --action backtest --strategy bb --symbol 510300 --start 20220101

# 组合策略回测
python main.py --action backtest --strategy combined --symbol 510300 --start 20220101

# 策略对比
python main.py --action backtest --strategy compare --symbol 510300 --start 20220101

# 回测并绘制净值曲线
python main.py --action backtest --strategy macd --symbol 510300 --start 20220101 --plot
```

### 6. 自定义参数

```bash
# 自定义回测参数
python main.py --action backtest --strategy macd --symbol 510300 \
  --start 20220101 --initial-cash 1000000 --commission 0.0005

# 自定义筛选参数
python main.py --action screen --strategy macd --lookback 90 --min-days 90
```

## 常见ETF代码

### 宽基指数
- 510050: 上证50ETF
- 510300: 沪深300ETF
- 510500: 中证500ETF
- 159901: 深证100ETF
- 588000: 科创50ETF

### 行业指数
- 512880: 证券ETF
- 512800: 银行ETF
- 512690: 酒ETF
- 515050: 科技ETF
- 159995: 芯片ETF
- 512170: 医药ETF

## 技术指标说明

### MACD
- **金叉**: MACD快线上穿慢线，买入信号
- **死叉**: MACD快线下穿慢线，卖出信号
- **零轴**: MACD在零轴上方为多头市场，下方为空头市场

### 布林带
- **上轨突破**: 价格突破上轨，可能进入超买区域
- **下轨突破**: 价格跌破下轨，可能进入超卖区域
- **带宽**: 布林带宽度，收缩后往往伴随趋势

## 注意事项

1. 本系统仅供学习研究使用，不构成投资建议
2. 数据来源于公开渠道，请自行验证数据准确性
3. 策略回测结果不代表未来表现
4. 实际交易需考虑滑点、手续费等成本
5. 请根据自身风险承受能力合理投资

## 许可证

MIT License
