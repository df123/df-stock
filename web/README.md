# Web 界面快速启动指南

## 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 启动步骤

### 1. 安装后端依赖

```bash
# 进入项目目录
cd /home/df/df-stock

# 安装依赖
pip install -r requirements.txt
```

### 2. 安装前端依赖

```bash
# 进入前端目录
cd web

# 安装依赖
npm install
```

### 3. 启动后端服务

```bash
# 方式1: 使用启动脚本（推荐）
./start_api.sh

# 方式2: 直接运行
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务将启动在 http://localhost:8000

### 4. 启动前端服务

```bash
cd web

# 开发模式
npm run dev
```

前端服务将启动在 http://localhost:8080

### 5. 访问系统

打开浏览器访问：
- 前端界面: http://localhost:8080
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 功能说明

### 仪表盘
- 数据库统计信息
- 涨幅前5名ETF
- 跌幅前5名ETF

### 实时行情
- 查看所有ETF实时行情
- 支持搜索ETF代码或名称
- 支持分页显示
- 自动更新（点击刷新按钮）

### 历史数据
- 查询指定ETF的历史数据
- 支持日期范围选择
- 显示开盘、最高、最低、收盘价
- 显示成交量和成交额

### 数据库管理
- 查看数据库统计信息
- 预览各类数据
- 数据导出功能

## 技术栈

### 后端
- FastAPI: 现代异步Web框架
- Uvicorn: ASGI服务器
- Pydantic: 数据验证
- SQLite: 数据库

### 前端
- Vue 3: 渐进式JavaScript框架
- Vite: 下一代前端构建工具
- Element Plus: Vue 3组件库
- Axios: HTTP客户端
- ECharts: 图表库

## 常见问题

### 后端启动失败
1. 检查端口8000是否被占用
2. 确保Python依赖已安装
3. 查看错误日志

### 前端启动失败
1. 检查端口8080是否被占用
2. 确保Node.js和npm已安装
3. 运行 `npm install` 安装依赖

### API请求失败
1. 确保后端服务已启动
2. 检查CORS配置
3. 查看浏览器控制台错误信息

## 开发建议

1. 修改代码后，前端会自动热更新
2. 后端修改后需要手动重启（如果使用--reload模式会自动重启）
3. 使用API文档测试接口: http://localhost:8000/docs
4. 数据库文件位于: `data/etf_data.db`

## 部署说明

### 生产环境部署

1. 前端构建：
```bash
cd web
npm run build
```

2. 前端使用Nginx部署（可选）

3. 后端使用Gunicorn部署：
```bash
pip install gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

4. 使用进程管理工具如supervisor或systemd

## 后续开发计划

- [ ] 技术指标分析页面
- [ ] ETF筛选功能
- [ ] 策略回测功能
- [ ] 图表可视化
- [ ] 数据导出优化
- [ ] 用户认证系统
- [ ] 告警功能
