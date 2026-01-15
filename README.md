# Option Strategy Serverless API on Vercel

This project demonstrates how to deploy a minimal option strategy API to Vercel.  It
leverages a simple `OptionStrategySystem` (copied from the root of the repository) and
exposes a serverless function at `/api/strategy` which returns the top strategy for
a given underlying symbol and objective.

## 项目结构

```
.
├── api
│   └── strategy.py             # Vercel Serverless 函数，用于后端逻辑
├── option_strategy_system.py   # 复制的后端模块
├── public
│   └── index.html             # 前端页面，用户交互界面
├── requirements.txt            # Python 依赖（可扩展）
└── vercel.json                 # Vercel 配置文件
```

## 本地运行

You can test the function locally using any WSGI server.  For example:

在本地测试 API 函数可以使用任何兼容 AWS Lambda 接口的服务器，或者直接部署到 Vercel 本地开发环境：

```bash
npm install -g vercel
vercel dev
```
Vercel 会自动启动本地开发服务器，你可以访问 `http://localhost:3000/` 看到前端页面，API 位于 `/api/strategy`。

## 部署到 Vercel

1. 安装 Vercel CLI：
   ```bash
   npm install -g vercel
   ```
2. 登录到你的 Vercel 账号：
   ```bash
   vercel login
   ```
3. 在 `vercel_option_strategy_app` 目录下执行：
   ```bash
   vercel
   ```
   按照提示创建一个新项目或关联到现有项目。Vercel 会根据 `vercel.json` 自动识别 Python 函数并部署，同时静态资源会被托管。
4. 部署完成后，访问 `https://<your-project>.vercel.app/` 即可看到前端页面；API 位于 `/api/strategy`，可以使用浏览器或 `curl` 测试。例如：
   ```bash
   curl "https://<your-project>.vercel.app/api/strategy?symbol=TSLA&objective=trend"
   ```
   响应中会包含推荐的策略名称、各腿参数及评分。

## Customisation

- **Enhancing DataEngine**: Replace the stub methods in `option_strategy_system.py`
  with actual calls to Interactive Brokers (IBKR) and Finnhub APIs to pull real
  market data.
- **Integrating OptionLab or py-vollib**: Add these libraries to
  `requirements.txt` and modify the `ScoreEngine` to compute probability of
  profit and risk metrics using OptionLab’s `run_strategy()` or py-vollib’s
  pricing functions.
- **Frontend UI**: Vercel also supports Next.js.  You can create a `pages`
  directory with React components to provide a user interface that calls this
  API.