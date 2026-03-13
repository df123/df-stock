#!/bin/bash

# 获取所有ETF历史数据到数据库
# 用法: ./scripts/fetch_all_etf.sh [start_date] [end_date] [start_code] [delay_seconds]

START_DATE=${1:-"20230101"}
END_DATE=${2:-""}
START_CODE=${3:-""}
DELAY=${4:-"0.5"}

cd /home/df/df-stock

LOG_FILE="logs/fetch_all_etf_$(date +%Y%m%d_%H%M%S).log"

echo "开始获取所有ETF历史数据..."
echo "日志文件: $LOG_FILE"
echo "参数: start_date=$START_DATE, end_date=$END_DATE, start_code=$START_CODE, delay=$DELAY"

python scripts/fetch_all_etf.py "$START_DATE" "$END_DATE" "$START_CODE" "$DELAY" > "$LOG_FILE" 2>&1

echo "完成！日志: $LOG_FILE"
tail -20 "$LOG_FILE"
