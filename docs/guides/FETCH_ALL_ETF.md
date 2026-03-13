# 获取所有ETF历史数据到数据库

## 当前状态

- **总ETF数量**: 1,447
- **已获取**: 349个ETF
- **剩余**: 1,098个ETF
- **预计时间**: 约12-15分钟（基于0.5秒延迟）

## 使用方法

### 方式1: 后台运行（推荐）

```bash
# 获取所有ETF（从2023年开始）
nohup ./scripts/fetch_all_etf.sh > logs/fetch_all.log 2>&1 &
echo $! > logs/fetch_all.pid

# 查看进度
tail -f logs/fetch_all.log

# 停止（如果需要）
kill $(cat logs/fetch_all.pid)
```

### 方式2: 命令行参数

```bash
# 完整命令
python scripts/fetch_all_etf.py [起始日期] [结束日期] [开始代码] [延迟秒数]

# 示例1: 获取所有ETF（2023-01-01 至今）
python scripts/fetch_all_etf.py 20230101

# 示例2: 指定时间范围
python scripts/fetch_all_etf.py 20230101 20250309

# 示例3: 从某个代码继续（断点续传）
python scripts/fetch_all_etf.py 20230101 "" sh510300

# 示例4: 调整延迟（加快速度）
python scripts/fetch_all_etf.py 20230101 "" "" 0.3
```

### 方式3: 使用Shell脚本

```bash
# 获取所有ETF
./scripts/fetch_all_etf.sh

# 指定参数
./scripts/fetch_all_etf.sh 20230101 "" "" 0.3
```

## 检查进度

```bash
# 查看数据库统计
python -c "
from data.database.db_manager import DatabaseManager
import sqlite3

db_manager = DatabaseManager()
conn = sqlite3.connect(db_manager.db_path)
cursor = conn.cursor()

cursor.execute('SELECT COUNT(DISTINCT code) FROM etf_history')
codes = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM etf_history')
records = cursor.fetchone()[0]

print(f'已获取ETF: {codes}/1447')
print(f'总记录数: {records}')

conn.close()
"

# 查看日志
tail -50 logs/fetch_all_etf_*.log | grep "处理\|成功\|失败"
```

## 参数说明

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| start_date | YYYYMMDD | 起始日期 | 20230101 |
| end_date | YYYYMMDD | 结束日期（空则今天） | 今天 |
| start_code | str | 从某个代码开始（断点续传） | 空 |
| delay_seconds | float | 每次请求延迟（秒） | 0.5 |

## 注意事项

1. **API限流**: 建议保持0.3-0.5秒延迟，避免触发限流
2. **磁盘空间**: 确保有足够空间（约100MB）
3. **网络稳定**: 任务运行期间保持网络连接
4. **断点续传**: 如中断，可用start_code参数从上次失败处继续
