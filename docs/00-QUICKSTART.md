# 00｜快速开始：Docker 全栈与原生开发

> 目标不是只看到首页，而是确认 Nginx、UI、API、PostgreSQL、Redis、Sandbox 和模型配置的关键链路都正确。本章提供两种方式：第一次运行推荐 Docker 全栈；需要逐行调试 Python/TypeScript 时再用原生开发模式。

## 1. 学习目标

完成本章后，你应该能够：

- 用一条脚本命令启动完整栈，并通过健康接口、日志和 UI 验证。
- 知道首次对话前必须配置 OpenAI 兼容模型，且不把密钥提交到 Git。
- 用 Docker 只启动 PostgreSQL、Redis、Sandbox，再在宿主机运行 FastAPI 与 Next.js。
- 解释 Docker 模式与原生模式为什么读取不同位置的 `.env`。
- 快速定位端口冲突、容器不健康、数据库密码不一致、模型调用失败和 VNC 失败。

## 2. 两种运行方式怎么选

| 方式 | 适合 | 优点 | 代价 |
|---|---|---|---|
| Docker 全栈（推荐） | 第一次运行、功能验收、稳定复现 | 版本与网络统一，静态沙箱开箱即用 | 首次构建 Sandbox 较慢；断点调试不如原生直接 |
| 原生 API/UI + Docker 基础设施 | 学 Python/FastAPI、React、热重载调试 | Uvicorn/Next 热更新，IDE 断点方便 | 要自己维护 Python、Node 和两套 `.env` |

当前默认 Compose 使用一个固定 Sandbox 容器，并把 Nginx 绑定到 `127.0.0.1`。这是适合可信本机学习的默认值，不是公网生产架构。

## 3. Docker 全栈：推荐路径

### 3.1 前置条件

- Windows：Docker Desktop 已安装并启动，使用 Linux containers。
- Linux：Docker Engine 与 Compose v2 插件。
- 建议至少预留 4 GB 可用内存和数 GB 镜像空间；Sandbox 包含 Ubuntu、Chromium、Node 和字体，首次构建明显慢于普通 API 镜像。

验证：

```powershell
docker version
docker compose version
```

若仓库尚未下载：

```powershell
git clone https://github.com/zzf-857/mooc-manus-learning.git
Set-Location mooc-manus-learning
```

以下命令默认当前目录已经是仓库根目录。

### 3.2 启动

Windows PowerShell：

```powershell
.\scripts\start.ps1
```

Linux/macOS/WSL：

```bash
bash ./scripts/start.sh
```

脚本会在缺失时从安全模板创建：

- 根目录 `.env` ← `.env.example`
- `api/config.yaml` ← `api/config.example.yaml`

然后校验 Compose、构建镜像并后台启动。不要把创建出的两个本地配置文件提交；仓库 `.gitignore` 已忽略它们。

等价的手动命令是：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path api/config.yaml)) { Copy-Item api/config.example.yaml api/config.yaml }
docker compose config --quiet
docker compose up -d --build
```

条件判断会保留已有本地配置。若要重新生成，请先人工备份，而不是直接覆盖可能包含密钥的文件。

### 3.3 等待健康检查

```powershell
docker compose ps
docker compose logs --tail 100 manus-api
```

期望核心服务逐步进入 `healthy`：

| 服务 | 验证内容 |
|---|---|
| `manus-postgres` | `pg_isready` |
| `manus-redis` | `redis-cli ping` |
| `manus-sandbox` | Supervisor 中全部进程就绪 |
| `manus-api` | `/api/status` 可访问 |
| `manus-ui` | Next.js 首页可访问 |
| `manus-nginx` | 依赖 UI/API 健康后启动入口 |

打开：

- 应用：`http://127.0.0.1:8088`
- API 文档：`http://127.0.0.1:8088/api/docs`
- 健康检查：`http://127.0.0.1:8088/api/status`

PowerShell 验证：

```powershell
Invoke-WebRequest http://127.0.0.1:8088 -UseBasicParsing
Invoke-RestMethod http://127.0.0.1:8088/api/status
.\scripts\doctor.ps1
```

`/api/status` 当前检查 PostgreSQL 与 Redis，不代表模型、Sandbox、文件存储、MCP 或 A2A 一定可用。完整验收还需要执行一次真实对话和一次文件上传。

### 3.4 配置模型

系统能在没有模型密钥时启动，但 Agent 对话会失败。推荐启动后在 UI 设置页填写：

- Base URL：OpenAI 兼容服务地址。
- API Key：只填入本地设置，不要粘贴到教程、Issue、截图或 Git。
- Model Name：支持 Chat Completions、工具调用与 JSON Object 输出的模型。
- Temperature 与 Max Tokens：先保留模板值，理解后再调。

也可以编辑本地 `api/config.yaml`，只参考结构：

```yaml
llm_config:
  base_url: "https://provider.example.invalid/v1"
  api_key: "<仅保存在本机的密钥>"
  model_name: "<支持工具调用的模型名>"
  temperature: 0.7
  max_tokens: 8192
```

`.invalid` 不是真实服务地址。真实配置请使用你自己的供应商信息，并确认其 OpenAI 兼容程度。修改后发起新请求会重新读取应用配置；已有运行中的 Task 仍使用创建时快照。

### 3.5 第一次功能验收

按顺序做：

1. 打开首页，创建新会话。
2. 输入一个无需联网的简单任务，例如让 Agent 创建一份短 Markdown 文件。
3. 观察 Plan、Step、Tool 事件是否逐步出现。
4. 打开会话文件列表，确认文件可预览/下载。
5. 打开 VNC 面板，确认可以看到 Sandbox 浏览器桌面。
6. 再测试一次网页访问或搜索，检查浏览器工具和网络。

默认 `FILE_STORAGE_BACKEND=local`，普通上传/下载不需要 COS 账号。当前浏览器工具截图 URL 的组装仍依赖 COS 配置；使用本地存储时，Agent 浏览器操作本身可执行，但工具卡片中的截图预览可能不可用。这是当前实现边界，不是启动失败。

### 3.6 常用运维命令

```powershell
# 查看状态
docker compose ps

# 查看所有日志
docker compose logs -f

# 只看某个服务
docker compose logs -f manus-api
docker compose logs -f manus-sandbox
docker compose logs -f manus-ui

# 重新构建并启动一个服务
docker compose up -d --build manus-api

# 停止并保留数据卷
.\scripts\stop.ps1

# 删除容器和数据卷：会清空 PostgreSQL、Redis 和本地文件，谨慎
docker compose down -v
```

Bash 使用 `bash ./scripts/stop.sh`。

### 3.7 默认网络边界

Compose 中 Nginx 端口映射为 `127.0.0.1:<端口>:80`，局域网其他机器无法直接访问。这是刻意的安全默认值。不要为了“能远程打开”就直接改成全网监听；当前项目尚未提供完整认证授权，开放前至少要增加反向代理认证、TLS、来源限制和对象级权限。

## 4. 原生开发：API/UI 热更新，基础设施用 Docker

### 4.1 前置条件

- Docker Desktop / Docker Engine。
- Python 3.12。
- [uv](https://docs.astral.sh/uv/)。
- Node.js 22 与 npm。

PowerShell 检查：

```powershell
python --version
uv --version
node --version
npm --version
docker version
```

仓库提供依赖安装脚本：

```powershell
.\scripts\setup.ps1
```

Bash：

```bash
bash ./scripts/setup.sh
```

它会执行 `uv sync --project api --frozen` 与 `npm ci --prefix ui`。原生模式仍需要 Docker，因为 PostgreSQL、Redis 和完整 Sandbox 由容器提供。

### 4.2 准备两套环境文件

根 `.env` 给 Docker Compose 和容器内 API 使用；`api/.env` 只在你从 `api/` 目录启动原生 Uvicorn 时由 Pydantic Settings 读取。

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
if (-not (Test-Path api/.env)) { Copy-Item api/.env.example api/.env }
if (-not (Test-Path api/config.yaml)) { Copy-Item api/config.example.yaml api/config.yaml }
```

然后检查 `api/.env`：

```dotenv
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://<用户>:<与根.env相同的数据库密码>@127.0.0.1:5432/<数据库名>
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
SANDBOX_ADDRESS=127.0.0.1
APP_CONFIG_FILEPATH=config.yaml
FILE_STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=.data/files
```

尖括号必须替换。两份示例文件中的数据库口令可能不同；原生 API 的 URI 必须与根 `.env` 中 Compose 创建 PostgreSQL 时使用的 `POSTGRES_USER/POSTGRES_PASSWORD/POSTGRES_DB` 一致，否则会出现密码认证失败。

### 4.3 只启动基础设施

```powershell
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build manus-redis manus-postgres manus-sandbox
docker compose -f docker-compose.yml -f docker-compose.dev.yml ps
```

开发覆盖文件只把基础设施端口发布到本机回环：

- PostgreSQL：`127.0.0.1:5432`
- Redis：`127.0.0.1:6379`
- Sandbox HTTP：`127.0.0.1:8080`
- Sandbox CDP：`127.0.0.1:9222`
- Sandbox VNC WebSocket：`127.0.0.1:5901`

验证 Sandbox：

```powershell
Invoke-RestMethod http://127.0.0.1:8080/api/supervisor/status
```

不要在原生模式启动 `manus-api/manus-ui/manus-nginx`，否则会和宿主机开发服务重复。

### 4.4 启动原生 API

新开一个终端：

```powershell
Set-Location api
$env:SQLALCHEMY_DATABASE_URI = 'postgresql+asyncpg://<用户>:<与根.env相同的数据库密码>@127.0.0.1:5432/<数据库名>'
uv sync --frozen
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Bash：

```bash
cd api
export SQLALCHEMY_DATABASE_URI='postgresql+asyncpg://<用户>:<与根.env相同的数据库密码>@127.0.0.1:5432/<数据库名>'
uv sync --frozen
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

尖括号必须替换。之所以还要把数据库 URI 导出为进程环境变量，是因为 API Settings 会读取 `api/.env`，但当前 `alembic/env.py` 只从进程环境读取覆盖值；如果只改 `.env`，启动迁移可能仍使用 `alembic.ini` 中面向容器网络的后备地址。

API 生命周期会自动执行 `alembic upgrade head`，然后初始化 Redis/PostgreSQL；本地存储模式不会初始化 COS。验证：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/status
Start-Process http://127.0.0.1:8000/api/docs
```

Python Playwright 这里只通过 CDP 连接 Sandbox Chromium，不需要在宿主机再执行 `playwright install`。

### 4.5 启动原生 UI

再开一个终端，必须显式指定 API 地址。当前前端不同模块的后备地址并不完全一致，显式设置可以确保聊天、文件下载和 VNC 都连到同一个 API。

PowerShell：

```powershell
Set-Location ui
$env:NEXT_PUBLIC_API_BASE_URL = 'http://127.0.0.1:8000/api'
npm ci
npm run dev
```

Bash：

```bash
cd ui
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api npm run dev
```

打开 `http://127.0.0.1:3000`。此时数据流是：

```text
浏览器 :3000 → FastAPI :8000 → PostgreSQL/Redis/Sandbox 容器
```

没有 Nginx，所以 UI 与 API 是跨端口请求；当前 API 的宽松 CORS 允许本地开发。该 CORS 设置不适合作为公网生产策略。

### 4.6 原生模式停止

在 API 与 UI 终端按 `Ctrl+C`，然后：

```powershell
Set-Location <仓库根目录>
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```

## 5. 开发验证命令

### API

```powershell
Set-Location api
uv run pytest -p no:cacheprovider -q
uv run python -m compileall -q app tests
```

### UI

```powershell
Set-Location ui
npm run lint
npm run build
```

### Sandbox

```powershell
Set-Location sandbox
uv run pytest -p no:cacheprovider -q
```

## 6. 常见问题

### 6.1 `api/config.yaml` 被挂载成目录

Compose 的 API volume 要求宿主路径是文件。如果首次启动前路径不存在，某些 Docker 环境可能创建目录。运行启动脚本让它从 `config.example.yaml` 创建文件；若已经误成目录，停止 Compose、确认其中无数据后人工移除目录并重新复制模板。

### 6.2 PostgreSQL `password authentication failed`

Docker 全栈使用根 `.env`。原生 API 使用 `api/.env`。确认 API URI 中用户、密码、数据库名与根 `.env` 完全一致。若你修改过密码但复用了旧数据卷，PostgreSQL 初始化密码不会自动改变；学习环境可在确认不需要数据后 `docker compose down -v` 重建。

### 6.3 API 容器不健康

```powershell
docker compose logs --tail 200 manus-api
docker compose logs --tail 100 manus-postgres
docker compose logs --tail 100 manus-redis
```

常见原因是数据库连接串错误、迁移失败、配置 YAML 格式错误。`/api/status` 只有在应用生命周期初始化完成后才可用。

### 6.4 Sandbox 长时间 building/starting

首次构建要下载 Ubuntu 软件、Chromium、Node 和字体。先看构建日志，不要反复重启。运行后检查：

```powershell
docker compose logs -f manus-sandbox
```

Supervisor 必须同时拉起 Xvfb、Chromium、CDP 代理、VNC、websockify 和 Sandbox API。

### 6.5 页面能开，但聊天立即失败

先检查模型 Key、Base URL、Model Name。当前 LLM 适配器需要兼容 OpenAI Chat Completions，并会使用工具、`response_format` 和关闭并行工具调用等参数；“能普通聊天”的模型网关不一定兼容 Agent 请求。

### 6.6 VNC 或浏览器工具失败

确认 Sandbox 健康，并检查 API 到 Sandbox 的三个通道：HTTP、CDP、VNC WebSocket。Docker 全栈使用容器名 `manus-sandbox`；原生开发必须让 `SANDBOX_ADDRESS=127.0.0.1`，且使用 dev Compose 发布端口。

### 6.7 端口被占用

```powershell
Get-NetTCPConnection -State Listen | Where-Object LocalPort -In 3000,5432,6379,8000,8080,8088,9222,5901
```

Docker 全栈通常只对宿主公开 Nginx 端口；原生模式才公开基础设施端口。

### 6.8 文件可上传但浏览器截图不显示

默认本地存储已经覆盖普通文件上传/下载。浏览器截图展示地址当前仍按 COS 域名组装；若未配置 COS，截图卡片可能是无效 URL。不要因此误判浏览器或 CDP 完全失效，先查看 Browser Tool 的文本结果和 VNC。

## 7. Unity 类比

| 当前项目 | Unity 开发体验 |
|---|---|
| Docker 全栈 | 打开一个固定版本的完整 Sample Project 直接 Play |
| 原生 API/UI | 进入 Editor、挂断点、启用 Domain Reload/热更新 |
| Compose healthcheck | 场景加载时等待 Addressables/网络服务 Ready |
| Nginx | 统一入口的 Gateway/反向代理，而不是业务脚本 |
| `.env` | 构建/运行环境参数，类似不同环境的 Build Profile |
| `config.yaml` | 可在运行时修改的游戏/Agent 配置资产 |
| Sandbox | 独立运行的受限游戏实例，不是主进程中的 Coroutine |

## 8. 练习

### 练习 1：完成双模式启动

先运行 Docker 全栈并完成一次对话；停止后再用原生 API/UI + Docker 基础设施启动。

验收：两种模式都能访问 UI、API docs 和状态接口，原生模式修改一个路由日志后 Uvicorn 会热重载。

### 练习 2：证明配置读取位置

在不写任何密钥的前提下，分别修改根 `.env` 与 `api/.env` 的 `LOG_LEVEL`，观察 Docker API 与原生 API 的日志差异。

验收：能解释为什么同名变量没有影响另一种运行模式。

### 练习 3：画启动依赖图

根据 Compose 的 `depends_on` 和 healthcheck，画出 Redis/PostgreSQL/Sandbox → API → UI → Nginx 的启动顺序。

验收：能解释容器“running”与服务“healthy”的区别。

## 9. 下一步

- 先理解服务边界：[01-ARCHITECTURE.md](./01-ARCHITECTURE.md)
- 再补 Python/FastAPI 基础：[02-PYTHON_FASTAPI.md](./02-PYTHON_FASTAPI.md)
- 配置模型、存储和远程工具：[03-CONFIGURATION.md](./03-CONFIGURATION.md)
