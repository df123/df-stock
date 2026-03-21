# AGENTS.md

## 项目概述

ETF量化分析系统是一个基于Python和Vue.js的量化分析平台，支持ETF数据获取、技术指标计算、策略回测和Web可视化。

## 构建/检查/测试命令

### 后端 (Python)
```bash
# 安装依赖
pip install -r requirements.txt

# 运行系统测试
python test_system.py

# 运行特定测试文件
python test_database.py
python test_offline.py

# 启动后端服务器（开发环境）
PYTHONPATH=/home/df/df-stock:$PYTHONPATH python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# 运行主CLI工具
python main.py --help
python main.py --action realtime --symbol 510300
python main.py --action indicators --symbol 510300 --start 20230101 --plot
python main.py --action backtest --strategy macd --symbol 510300 --start 20230101
```

### 前端 (Vue.js)
```bash
# 安装依赖
cd web && npm install

# 启动开发服务器
npm run dev

# 生产环境构建
npm run build

# 预览生产构建
npm run preview
```

### 一键启动服务
```bash
# 使用一键启动脚本（推荐）
./scripts/start.sh

# 脚本功能：
# 1. 检查端口占用（8000和8080端口）
# 2. 自动关闭已占用端口的进程
# 3. 启动后端API服务（端口8000）
# 4. 启动前端Web服务（端口8080）
# 5. 输出服务地址和日志位置

# 查看服务日志
tail -f logs/api.log    # 后端日志
tail -f logs/web.log    # 前端日志

# 停止服务
kill <API_PID> <WEB_PID>  # 使用脚本输出的PID
```

### 测试单独组件
```bash
# 测试数据获取
python test_offline.py

# 测试数据库操作
python test_database.py

# 测试完整系统集成
python test_system.py

# 运行测试文件中的特定函数（修改测试文件调用特定函数）
python test_system.py
```

### 数据更新
```bash
# 增量更新所有ETF数据（仅更新新数据）
python scripts/incremental_update.py

# 增量更新指定ETF
python scripts/incremental_update.py --codes 510300 510500

# 使用Shell脚本更新
./scripts/incremental_update.sh
./scripts/incremental_update.sh 510300 510500

# 获取所有ETF历史数据
python scripts/fetch_all_etf.py

# 使用Shell脚本获取所有ETF
./scripts/fetch_all_etf.sh
```

## 代码风格指南

### Python

#### 导入语句
- 顺序：标准库 → 第三方库 → 本地模块
- 使用项目根目录的绝对导入本地模块
- 各组之间用空行分隔
```python
import pandas as pd
from datetime import datetime
from typing import Optional, List
from data.etf_data_fetcher import ETFDataFetcher
from config import Config
```

#### 命名约定
- **类名**：PascalCase（如 `ETFDataFetcher`, `VisualizationUtils`, `BacktestEngine`）
- **函数/方法**：snake_case（如 `get_etf_list`, `calculate_macd`, `save_to_db`）
- **变量**：snake_case（如 `realtime_data`, `initial_cash`）
- **常量**：Config类中使用UPPER_SNAKE_CASE（如 `MACD_DEFAULT_FAST`, `DEFAULT_COMMISSION`）

#### 类型提示
- 总是为函数参数和返回值使用类型提示
- 可空参数使用 `Optional`
- pandas返回类型使用 `-> pd.DataFrame`
```python
def get_etf_history(
    self,
    symbol: str,
    start_date: str,
    end_date: Optional[str] = None,
    period: str = 'daily',
    save_to_db: bool = True
) -> pd.DataFrame:
```

#### 文档字符串
- 使用三引号文档字符串和中文描述
- 在相关位置包含参数说明
- 使用外部API时注明数据源
```python
def get_etf_realtime(self, symbol: Optional[str] = None) -> pd.DataFrame:
    """
    获取ETF实时净值数据
    数据源: 同花顺（基金净值数据）
    
    Args:
        symbol: ETF代码（可选）
    """
```

#### 错误处理
- 对外部API调用和数据库操作使用try-except块
- 尽可能捕获特定异常，回退到Exception
- 失败时返回空DataFrame或None，打印错误信息
```python
try:
    df = ak.fund_etf_spot_ths()
    return df
except Exception as e:
    print(f"获取实时数据失败: {e}")
    return pd.DataFrame()
```

#### Pandas DataFrame约定
- 使用中文列名：'代码', '名称', '最新价', '涨跌幅'
- 处理前总是检查 `if df.empty`
- 使用 `.copy()` 避免SettingWithCopyWarning
- 使用 `pd.to_numeric()` 进行类型转换，参数设为 `errors='coerce'`

#### FastAPI/Pydantic
- 使用Pydantic模型验证所有API请求/响应
- 使用 `Field(..., description="...")` 编写文档
- 包含 `Config.from_attributes = True` 以支持ORM
```python
class RealtimeData(BaseModel):
    code: str = Field(..., description="ETF代码")
    price: Optional[float] = Field(None, description="最新价")
```

### Vue.js

#### 文件结构
- 视图组件：`/web/src/views/` - 主要页面组件（Dashboard.vue, Realtime.vue等）
- API：`/web/src/api/` - API端点定义
- 路由：`/web/src/router/index.js` - 路由配置

#### Vue Composition API
- 使用 `<script setup>` 语法
- 原始类型使用 `ref`，对象使用 `reactive`
- 使用别名解构API以提高清晰度
```javascript
import { ref, onMounted } from 'vue'
import { realtimeAPI } from '@/api/endpoints'

const loading = ref(false)
const data = ref([])
```

#### 组件命名
- 文件名和组件名使用PascalCase
- 根据功能使用描述性名称（Realtime.vue, History.vue, Database.vue）

#### API调用
- 使用来自 `/api/index.js` 的axios实例，配置base URL
- 在拦截器中处理错误，检查 `response.success`
- 使用try-catch并记录错误
```javascript
try {
  const response = await realtimeAPI.getAll()
  if (response.success) {
    data.value = response.data
  }
} catch (error) {
  console.error('加载数据失败:', error)
}
```

#### Element Plus
- 使用Element Plus作为UI组件库
- 遵循Element Plus组件约定（el-table, el-button, el-form）
- 为组件特定CSS使用作用域样式

#### 样式
- 在 `<style scoped>` 块中使用作用域样式
- 布局使用Flexbox（display: flex, justify-content, align-items）
- 考虑移动端响应式

## 项目结构

```
api/                    # FastAPI后端
├── main.py            # FastAPI应用入口
├── models/            # Pydantic模型
├── routers/           # API路由处理器（realtime, history, database）
└── config.py          # API配置

web/                   # Vue.js前端
└── src/
    ├── api/          # API客户端
    ├── router/       # Vue Router
    └── views/        # 页面组件

data/                  # 数据获取（AKShare）
indicators/            # 技术指标（MACD, 布林带, RSI）
strategies/            # 交易策略
backtest/             # 基于Backtrader的回测
screening/            # ETF筛选
utils/                # 工具函数（可视化、日期工具）
config.py             # 全局配置
main.py               # CLI入口点
```

## 重要注意事项

- 后端需要设置 `PYTHONPATH=/home/df/df-stock` 用于模块导入
- 前端代理配置到 `/api` 用于后端通信
- 数据库使用SQLite，位于 `db/etf_data.db`
- 数据源：新浪财经（ETF列表、历史数据），同花顺（实时净值）
- 禁止使用东方财富（东财）数据源
- 部署更改前总是使用 `python test_system.py` 测试
- 前端开发服务器运行在8080端口，后端运行在8000端口

**根目录管理规范：**
- ✅ 根目录仅保留：`AGENTS.md`（开发指南）、`README.md`（项目说明）
- ✅ 其他文档统一存放：`docs/` 文件夹
  - `docs/implementation/` - 实现文档（IMPLEMENTATION_SUMMARY.md、WEB_IMPLEMENTATION.md等）
  - `docs/guides/` - 功能指南（DATABASE_USAGE.md、DATA_SOURCE_UPDATE.md等）
- ✅ 保持根目录简洁：避免创建临时文件、测试输出文件直接存放在根目录

**日志文件管理规范：**
- ✅ 日志文件统一存放：`logs/` 文件夹
  - `logs/api.log` - 后端API服务日志
  - `logs/web.log` - 前端开发服务日志
- ✅ 启动脚本应配置日志输出到 `logs/` 目录
- ✅ 避免在根目录创建 `.log` 文件

**脚本文件管理规范：**
- ✅ Shell脚本统一存放：`scripts/` 文件夹
  - `scripts/install.sh` - 环境依赖安装脚本
  - `scripts/start.sh` - 一键启动脚本（推荐使用）
  - `scripts/start_api.sh` - 后端API服务启动脚本
  - `scripts/start_web.sh` - Web服务启动指南脚本
- ✅ 所有 `.sh` 文件应添加可执行权限：`chmod +x scripts/*.sh`
- ✅ 启动服务时推荐使用一键启动脚本：`./scripts/start.sh`

**数据库文件管理规范：**
- ✅ 数据库文件统一存放：`db/` 文件夹
  - `db/etf_data.db` - SQLite数据库文件
- ✅ 数据库路径配置在 `config.py` 中：`DB_PATH`
- ✅ 使用 `.gitkeep` 保持目录结构追踪
- ✅ 所有 `.db` 文件已在 `.gitignore` 中忽略，不提交实际数据库文件

