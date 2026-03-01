# SQLite 数据库功能使用说明

## 功能概述

本项目已集成 SQLite 数据库支持，可以自动将抓取的数据保存到本地数据库，方便您复盘和分析。

## 数据库位置

数据库文件位于：`data/etf_data.db`

## 数据表结构

### 1. etf_list - ETF基本信息表
- `code`: ETF代码
- `name`: ETF名称
- `fund_type`: 基金类型
- `created_at`: 创建时间
- `updated_at`: 更新时间

### 2. etf_realtime - 实时行情快照表
- `code`: ETF代码
- `name`: ETF名称
- `price`: 最新价
- `change_percent`: 涨跌幅
- `change_amount`: 涨跌额
- `data_date`: 数据日期
- `fund_type`: 基金类型
- `snapshot_date`: 快照日期
- `snapshot_time`: 快照时间
- `created_at`: 创建时间

### 3. etf_history - 历史行情表
- `code`: ETF代码
- `date`: 日期
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价
- `volume`: 成交量
- `amount`: 成交额
- `created_at`: 创建时间

### 4. screening_results - 筛选结果表
- `strategy`: 策略类型
- `code`: ETF代码
- `name`: ETF名称
- `signal_type`: 信号类型
- `price`: 价格
- `change_percent`: 涨跌幅
- `lookback_days`: 回溯天数
- `screen_date`: 筛选日期
- `screen_time`: 筛选时间
- `created_at`: 创建时间

### 5. backtest_results - 回测结果表
- `strategy`: 策略类型
- `code`: ETF代码
- `start_date`: 开始日期
- `end_date`: 结束日期
- `initial_cash`: 初始资金
- `final_value`: 最终价值
- `total_return`: 总收益率
- `max_drawdown`: 最大回撤
- `sharpe_ratio`: 夏普比率
- `win_rate`: 胜率
- `total_trades`: 交易次数
- `commission_rate`: 手续费率
- `run_date`: 运行日期
- `run_time`: 运行时间
- `created_at`: 创建时间

## 使用方法

### 1. 自动保存数据

所有数据查询操作都会自动保存到数据库：

```bash
# 查询实时行情（自动保存）
python main.py --action realtime --symbol 510300

# 查询历史数据（自动保存）
python main.py --action history --symbol 510300 --start 20240101 --end 20240226

# 技术指标分析（自动保存）
python main.py --action indicators --symbol 510300 --start 20240101
```

### 2. 数据库查询

使用 `--action db-query` 命令查询数据库中的数据：

```bash
# 查看数据库统计信息
python main.py --action db-query

# 查询实时行情数据
python main.py --action db-query --table etf_realtime --symbol 510300 --rows 10

# 查询历史数据
python main.py --action db-query --table etf_history --symbol 510300 --start-date 2024-02-01 --end-date 2024-02-26

# 查询筛选结果
python main.py --action db-query --table screening_results --strategy macd
```

### 3. 数据导出

将查询结果导出为CSV文件：

```bash
# 导出查询结果
python main.py --action db-query --table etf_realtime --symbol 510300 --export-csv

# 直接从数据库导出整个表
python -c "from data.database import DatabaseManager; db = DatabaseManager(); print(db.export_to_csv('etf_history'))"
```

### 4. 筛选和回测结果保存

执行筛选和回测时，结果也会自动保存到数据库：

```bash
# 筛选ETF（结果自动保存）
python main.py --action screen --strategy macd --lookback 60 --save

# 策略回测（结果自动保存）
python main.py --action backtest --strategy macd --symbol 510300 --start 20240101 --end 20240226
```

## 数据去重机制

系统采用智能去重机制：

1. **实时数据**：根据 `代码 + 快照日期` 组合去重，同一天多次查询会覆盖之前的数据
2. **历史数据**：根据 `代码 + 日期` 组合去重，相同日期的历史数据不会重复保存

## 配置选项

在 `config.py` 中可以配置数据库相关选项：

```python
DB_PATH = 'data/etf_data.db'  # 数据库文件路径
DB_ENABLED = True              # 是否启用数据库功能
```

## 命令行参数

### db-query 专用参数

- `--table`: 指定查询的表名（etf_history, etf_realtime, screening_results, backtest_results）
- `--symbol`: 指定ETF代码
- `--date`: 指定日期（格式：YYYY-MM-DD）
- `--start-date`: 指定开始日期（格式：YYYY-MM-DD）
- `--end-date`: 指定结束日期（格式：YYYY-MM-DD）
- `--rows`: 指定显示行数
- `--export-csv`: 导出查询结果到CSV文件

## 数据库管理

### 直接访问数据库

您可以使用任何 SQLite 客户端访问数据库：

```bash
# 使用 sqlite3 命令行工具
sqlite3 data/etf_data.db

# 使用 Python 脚本
python -c "from data.database import DatabaseManager; db = DatabaseManager(); print(db.get_stats())"
```

### 数据库备份

定期备份数据库文件：

```bash
cp data/etf_data.db data/etf_data_backup_$(date +%Y%m%d).db
```

## 常见使用场景

### 场景1：每日收盘后抓取数据

```bash
# 抓取所有ETF的实时行情
python main.py --action realtime

# 查看数据统计
python main.py --action db-query
```

### 场景2：复盘某只ETF的历史表现

```bash
# 查询历史数据
python main.py --action db-query --table etf_history --symbol 510300 --start-date 2024-01-01 --end-date 2024-02-26

# 导出数据到CSV进行进一步分析
python main.py --action db-query --table etf_history --symbol 510300 --export-csv
```

### 场景3：分析策略表现

```bash
# 查看所有筛选结果
python main.py --action db-query --table screening_results

# 查看特定策略的结果
python main.py --action db-query --table screening_results --strategy macd

# 查看回测结果
python main.py --action db-query --table backtest_results --strategy macd
```

## 注意事项

1. 数据库文件位于 `data/` 目录下，请确保该目录有写入权限
2. 数据文件可能会随着使用增长，建议定期清理或备份
3. 如果不需要数据库功能，可以在 `config.py` 中设置 `DB_ENABLED = False`
4. 数据库采用 SQLite 格式，兼容所有标准 SQLite 工具
