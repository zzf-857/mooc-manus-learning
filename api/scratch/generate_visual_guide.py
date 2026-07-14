#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json

# 项目基础路径 (自动定位到当前脚本所在的项目根目录)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# HTML 导航输出路径 (直接生成在 scratch 目录下)
OUTPUT_HTML = os.path.join(PROJECT_ROOT, "scratch", "project_structure.html")

# 定义高层分层 layer 标签
LAYERS = {
    "app/interfaces": "interfaces",
    "app/application": "application",
    "app/domain": "domain",
    "app/infrastructure": "infrastructure"
}

# 静态描述与 Unity 类比字典
STATIC_DETAILS = {
    "mooc-manus (项目根目录)": {
        "title": "项目根目录",
        "badge": "Project Root",
        "desc": "整个 MoocManus Agent 后端服务（API）的物理根目录。它汇总了所有后端代码、迁移文件、第三方依赖管理配置以及运行守则。",
        "analogy": "<b>Unity Project Root Folder：</b> 相当于你 Unity 游戏工程的根目录，里面包含了 Assets (核心代码 and 资源)、Packages (外部依赖包) 和 ProjectSettings 等外围配置。",
        "files": "主要由项目包描述 <code>pyproject.toml</code>、锁定依赖 <code>uv.lock</code> 以及 AI 行为守则 <code>AGENTS.md</code> 等文件组成。"
    },
    ".env.example": {
        "title": "环境变量安全模版 (.env.example)",
        "badge": "Env Template",
        "desc": "本地环境变量的安全配置模版，不含任何真实的 API Key 等敏感密匙。作为代码共享时配置参考使用。",
        "analogy": "<b>只读配置模版：</b> 类似于你游戏的本地只读配置模版。规定了需要配置哪些主机 IP、端口等键名，但真实的游戏运行凭证需要各自本地补充。",
        "files": "用于指示团队成员本地创建 <code>.env</code> 文件。"
    },
    ".gitignore": {
        "title": "Git 忽略配置 (.gitignore)",
        "badge": "Git Config",
        "desc": "配置哪些本地产生的文件（如虚拟环境、缓存、本地敏感密钥配置文件等）绝对不能被提交到 Git 版本控制仓库中。",
        "analogy": "<b>Git 排除规则：</b> 类似于 Unity 项目在提交 Git 时，一定要把 <code>Library/</code> 临时运行目录、本地编译产生的 <code>Temp/</code> 缓存、以及 <code>LocalOnlySettings</code> 配置文件排除，防止发生合并冲突和密钥泄露。",
        "files": "配置项包括：<code>.venv/</code>、<code>__pycache__/</code>、<code>config.yaml</code> 等。"
      },
      ".python-version": {
        "title": "Python 运行时声明 (.python-version)",
        "badge": "Python Env",
        "desc": "声明本项目开发及运行所需的精确 Python 版本号（如 3.12.x）。",
        "analogy": "<b>Unity Target Runtime Version：</b> 类似于在 Unity 中指定的工程目标 Unity 引擎版本（如 2022.3.LTS），确保所有的协同开发者都在同一基础环境下工作，杜绝因引擎版本升级带来的 api 不兼容报错。",
        "files": "内容为版本号，用于 uv/pyenv 依赖管理器。"
      },
      "Dockerfile": {
        "title": "容器化部署脚本 (Dockerfile)",
        "badge": "Docker Build",
        "desc": "定义后端服务如何在轻量级容器（Docker）里一键安装依赖、拷入代码并启动运行的编译蓝图。",
        "analogy": "<b>平台打包配置 (Build Pipeline Script)：</b> 类似你 Unity 项目中编写的一键打包编译脚本。该脚本规定如何拷贝编译资源、在无尘的隔离环境中打包出可以直接运行的 exe/apk 游戏安装包。",
        "files": "定义了多阶段编译（Multi-stage build）以缩小最终镜像大小。"
      },
      "README.md": {
        "title": "项目说明白皮书 (README.md)",
        "badge": "Documentation",
        "desc": "项目的基础介绍、本地环境一键配置命令、以及服务运行架构设计的速查手册。",
        "analogy": "<b>工程引导手册：</b> 类似于你在游戏工程根目录下保留的 <code>README.txt</code> 说明书，新入职的程序可以通过该手册最快熟悉这个游戏的架构和跑通本地 Play 模式的方法。",
        "files": "Markdown 编写的项目自述文件。"
      },
      "alembic.ini": {
        "title": "Alembic 全局迁移配置 (alembic.ini)",
        "badge": "Config / Alembic",
        "desc": "这是 SQLAlchemy Alembic 数据库版本控制与迁移工具的全局配置文件。它指明了迁移文件的物理生成目录、数据库的连接字符串（sqlalchemy.url）以及迁移执行时的日志捕获格式。",
        "analogy": "<b>存档版本升级配置文件：</b> 类似于游戏存档系统的全局升级配置。当游戏从 1.0 升级到 2.0，老存档数据结构需要升级时，该配置文件指导升级工具如何去建立老数据到新数据的迁移桥梁。",
        "files": "主要配置项：<code>script_location = alembic</code>（迁移脚本路径）、<code>sqlalchemy.url</code>（本地 Postgres 的连接字符串）。"
      },
      "alembic/README": {
        "title": "Alembic 自述文件",
        "badge": "Alembic Doc",
        "desc": "Alembic 数据库迁移的说明自述，指导如何生成和应用新一轮的迁移脚本。",
        "analogy": "<b>数据库维护说明：</b> 告知开发人员如何操作数据库升级脚本命令的备忘说明。",
        "files": "Alembic 系统默认生成的静态文档。"
      },
      "alembic/env.py": {
        "title": "Alembic 数据库环境加载器 (env.py)",
        "badge": "Alembic Engine",
        "desc": "每次执行数据库表迁移时运行的底层 Python 脚本。它负责连接物理数据库、捕获我们 Python 里的数据表模型元数据，并执行升级（upgrade）或降级（downgrade）事务操作。",
        "analogy": "<b>存档升级机制驱动类：</b> 类似于在 Unity 中具体执行数据反序列化与旧表字段重构的底层驱动器，它动态去读写玩家的历史本地存档，安全地执行字段扩容。",
        "files": "通过载入 <code>app.infrastructure.models.base</code> 元数据进行自动物理建表。"
      },
      "alembic/script.py.mako": {
        "title": "迁移脚本模版 (script.py.mako)",
        "badge": "Alembic Template",
        "desc": "Alembic 在自动生成每一次版本升级脚本时，所套用的 Python 代码骨架模版。",
        "analogy": "<b>代码生成模版 (Script Template)：</b> 类似于你在 Unity 中自定义的 C# 脚本模板。每当你在 Assets 目录里新建脚本时，自动预装好 copyright 声明、命名空间、以及默认的 Awake 方法的模板文件。",
        "files": "Mako 模板语法，定义了 migration 文件的默认骨架。"
      },
      "app/main.py": {
        "title": "应用启动主入口 (main.py)",
        "badge": "Entry Point",
        "desc": "FastAPI 服务的生命周期启动与配置主干。负责创建全局 FastAPI 实例，挂载跨域 CORS 中间件，包含总路由表的挂载，以及管理服务启动与关闭时的资源（如数据库会话池、缓存连接）的生命周期（lifespan）。",
        "analogy": "<b>游戏主启动脚本 (GameBootstrap)：</b> 类似于你挂载在游戏初始化场景（InitScene）的 <code>GameBootstrap.cs</code>，负责最先执行 `Awake()`。在其中配置第三方 SDK 初始化、建立网络 Socket连接、启动首屏 UI，并且在游戏退出时释放资源。",
        "files": "启动运行指令：通过 <code>uvicorn app.main:app --reload</code> 唤醒并维持该主循环进程。"
      },
      "core/config.py": {
        "title": "核心系统配置类 (config.py)",
        "badge": "Global Config",
        "desc": "存放项目最底层的全局配置和环境变量解析。负责从系统环境变量或本地的 <code>.env</code> 文件中提取敏感密匙（如 API Key、数据库密码、Redis 连接等），提供强类型对象支持。",
        "analogy": "<b>全局配置 ScriptableObject：</b> 类似于你在 Unity 中建立的 GameSettingsSO 或全局的 AppConst，统一放置当前是开发环境还是正式环境、服务器 IP 端口、大模型的全局默认超参参数等。",
        "files": "核心文件：<code>config.py</code>（定义了继承自 Pydantic <code>BaseSettings</code> 的 Settings 类）。"
      },
      "dev.sh": {
        "title": "开发辅助脚本 (dev.sh)",
        "badge": "Shell Script",
        "desc": "用于在类 Unix 平台下一键启动本地开发环境，如数据库容器建立、依赖自动注入等。",
        "analogy": "<b>本地运行辅助工具：</b> 类似你在 Unity 编译器下编写的快捷 Editor 窗口工具，一键打开测试关卡、预载入测试玩家数值。",
        "files": "Shell 批处理脚本。"
      },
      "run.sh": {
        "title": "生产服务运行脚本 (run.sh)",
        "badge": "Shell Script",
        "desc": "在部署服务器上拉起 FastAPI 后端进程的启动批处理指令。",
        "analogy": "<b>一键运行可执行程序：</b> 相当于打包出 zip 包后附带的 <code>StartGame.sh</code>，玩家运行它即可自动拉起核心的游戏主程序。",
        "files": "Shell 脚本。"
      },
      "pyproject.toml": {
        "title": "项目依赖描述文件 (pyproject.toml)",
        "badge": "Package Manifest",
        "desc": "现代 Python 项目的规范依赖和打包配置文件。详细记载了项目元数据（作者、版本、许可证）以及项目所运行需要的所有第三方库（FastAPI、SQLAlchemy、pydantic 等）。",
        "analogy": "<b>Unity Packages Manifest (manifest.json)：</b> 类似于你 Unity 工程里 `Packages` 目录下的 <code>manifest.json</code>，负责向 Unity 声明并下载该项目所运行需要的所有外部 Unity Package（如 InputSystem, ProBuilder 等）。",
        "files": "主要配置项：<code>dependencies = [...]</code> 声明依赖包列表。"
      },
      "uv.lock": {
        "title": "依赖精确锁文件 (uv.lock)",
        "badge": "Lock File",
        "desc": "记录当前项目已安装的每一个 Python 库及其所有子依赖的**精确版本和哈希值**。由 uv 依赖管理器自动生成，确保无论在谁的电脑上部署，安装出来的环境都完全一致。",
        "analogy": "<b>Packages 锁文件 (packages-lock.json)：</b> 类似于 Unity 项目在解析并锁定 package 版本后生成的 <code>packages-lock.json</code>，记录每个组件的绝对准确版本，防止他人拉取代码后因包版本更新而导致编译报错。",
        "files": "该文件由 uv 工具全自动维护，不应手动修改。"
      },
      "AGENTS.md": {
        "title": "AI 开发者协同规范 (AGENTS.md)",
        "badge": "AI Rules",
        "desc": "专门针对协作本项目的 AI 编码助手（如当前的我）编写的行为操守与开发章程。核心是要求 AI 修改任何核心业务代码前，必须征得用户的明确授权同意，防范无序改动。",
        "analogy": "<b>团队编码行为守则 (Coding Convention Guidelines)：</b> 类似于主程写给团队程序员（含 AI 与外包）的协同开发规定，避免乱改架构导致功能冲突，保证核心业务质量。",
        "files": "定义了严格的带学协作模式。"
      },
      "pytest.ini": {
        "title": "测试框架全局配置 (pytest.ini)",
        "badge": "Test Config",
        "desc": "配置 pytest 测试套件的启动行为、指定测试搜索的文件规范、以及控制打印日志到控制台的配置器。",
        "analogy": "<b>Unity Test Runner 设定：</b> 类似于你针对 Unity Editor 下的测试运行面板所做的过滤项，例如屏蔽某些慢场景加载测试，开启特定的断言断点输出。",
        "files": "定义了 `python_files = test_*.py` 等执行规则。"
      },
      "tests/conftest.py": {
        "title": "单元测试公共脚手架 (conftest.py)",
        "badge": "Test Fixtures",
        "desc": "存放全局共享的测试桩（Fixtures）。例如在跑测试用例前自动创建一个临时内存数据库连接池、动态配置 Redis 客户端桩等，为所有 test 文件提供环境支持。",
        "analogy": "<b>自动化测试的基础环境初始化器 (Test Setup Controller)：</b> 类似于在 Unity 测试套件中专门配置的 `Setup()` 全局静态脚本，在运行测试场景前自动把虚拟关卡、测试玩家和测试存档数据一键生成好。",
        "files": "通过 pytest 提供的 `fixture` 机制向各测试用例函数注入依赖。"
      },
      "tests/app/interfaces/endpoints/test_status_routes.py": {
        "title": "健康接口自动化测试用例 (test_status_routes.py)",
        "badge": "Unit Test",
        "desc": "编写具体的单元测试代码，发起模拟的 HTTP 请求访问 <code>/api/status</code>，并校验其返回状态码是否为 200，统一数据返回包里的 `code` 是否是 200。",
        "analogy": "<b>关卡启动与接口功能测试用例 (PlayMode Test Case)：</b> 类似于你写的一个 PlayMode 测试用例，自动模拟运行游戏，启动主界面并判定『网络是否成功连上』，如果连上就标记 PASS，否则直接报警红字。",
        "files": "包含使用 `httpx.AsyncClient` 进行的异步接口请求测试。"
      },
      "app/interfaces/service_dependencies.py": {
        "title": "依赖注入服务管理类 (service_dependencies.py)",
        "badge": "Dependency Injection",
        "desc": "FastAPI 的核心机制之一（Depends）。在这里统一组织并动态生成业务所需的依赖对象（如当前的数据库 session、Redis 客户端、应用 Service 实例），生命周期随请求自动建立和销毁。",
        "analogy": "<b>依赖注入 / GetComponent 动态分配器：</b> 类似于你在 Unity 中设计了一个辅助类动态去拿组件：<code>GetComponent<SqlConnection>()</code>。当你当前脚本需要用到数据库时，通过该机制自动把当前激活的物理连接分发给你，用完后自动回收。",
        "files": "定义了 <code>get_db_session()</code>、<code>get_status_service()</code> 等方法供路由层动态调用。"
      },
      "app/interfaces/endpoints/routes.py": {
        "title": "总 API 路由表聚合中心 (routes.py)",
        "badge": "API Router Gateway",
        "desc": "整个后端对外的所有功能路由接口的『聚合网关』。它将各个子路由模块（健康度、配置管理等）统一聚合成一个大的总 APIRouter 挂载到主入口上。",
        "analogy": "<b>UI 界面主路由事件管理器 (MainMenuRouter)：</b> 类似于游戏的全局 UI 控制路由器。不管玩家是要进入『设置界面』、『存档界面』还是『关卡主界面』，都在这里注册它们点击事件对应的处理脚本入口。",
        "files": "聚合了 status 路由和 app-config 路由。"
      },
      "app/interfaces/endpoints/app_config_routes.py": {
        "title": "全局配置路由接口 (app_config_routes.py)",
        "badge": "HTTP Routes",
        "desc": "监听 <code>GET /api/app-config/llm</code> 及 <code>POST /api/app-config/llm</code> 两个网络路径，负责前端修改系统大模型密钥、模型类型时的数据吞吐入口。",
        "analogy": "<b>设置界面 UI 点击响应脚本 (SettingsUIPanel)：</b> 监听玩家在设置里修改『画面质量』、『服务器端口』、『语言』的输入，并在点保存时将其打包发给后台的管理器处理。",
        "files": "配合 <code>AppConfigService</code> 工作流程层完成配置读写操作。"
      },
      "app/interfaces/endpoints/status_routes.py": {
        "title": "系统状态路由接口 (status_routes.py)",
        "badge": "HTTP Routes",
        "desc": "监听 <code>GET /api/status</code> 路径，向前端或监测服务器返回当前 API 进程是否存活、底层物理 PostgreSQL 和 Redis 是否正常连接的诊断数据。",
        "analogy": "<b>系统诊断 UI 面板 (DiagnosticPanel)：</b> 游戏内按 F3 调出的系统性能面板，实时向玩家展示：『当前网络延迟几毫秒』、『本地物理数据库连接是否成功』、『云端同步是否成功』。",
        "files": "使用 <code>StatusService</code> 聚合底层各个真实组件的检测器进行诊断。"
      },
      "app/interfaces/errors/exception_handlers.py": {
        "title": "FastAPI 全局异常拦截注册 (exception_handlers.py)",
        "badge": "API Exception Handler",
        "desc": "将后端代码在运行过程中抛出的应用级或领域级异常（如 NotFoundException），自动捕获并转换成对前端极其友好的 HTTP 400/500 JSON 状态响应。",
        "analogy": "<b>UI 全局弹窗系统 / 崩溃捕获器：</b> 类似于在 Unity 中利用 <code>Application.logMessageReceived</code> 捕获全局空指针或致命报错，并展示出一个精美的『网络异常，请重试』UI 弹窗，而不是直接让玩家看到刺眼的红字堆栈或导致游戏闪退。",
        "files": "注册并捕获 <code>AppException</code> 及标准 Python 运行时异常。"
      },
      "app/interfaces/schemas/base.py": {
        "title": "统一 API 响应契约模型 (base.py)",
        "badge": "Pydantic Schema",
        "desc": "定义了该 API 后端框架下，所有对接口成功、失败、数据返回时，外围 JSON 包体统一的长相，定义了统一的 code, msg 和 data 字段。",
        "analogy": "<b>网络下行数据包体模版 (BaseNetworkResponsePacket)：</b> 类似于你写好的通信基类包，所有的网络下行包都强制包含 <code>int ErrorCode</code>、<code>string ErrorMsg</code>、<code>T Data</code>。这有利于客户端前端一劳永逸地适配错误弹窗。",
        "files": "使用 Pydantic <code>BaseModel</code> 定义了强类型的 <code>Response</code> 实体。"
      },
      "app/application/errors/exceptions.py": {
        "title": "应用级流程异常定义 (exceptions.py)",
        "badge": "App Exceptions",
        "desc": "定义了各种在业务流程中违反规则时的异常（如配置不存在、服务不可达等），便于外围统一捕捉为对应的 HTTP 状态码。",
        "analogy": "<b>游戏业务逻辑错误定义 (Quest/Flow Exception)：</b> 类似于你在做任务系统时自定义的 <code>QuestFinishedException</code>（任务已完成不能重复交）或者是 <code>InventoryFullException</code>（背包已满无法添加装备），用于精准表示游戏内逻辑流程出错。",
        "files": "自定义了 <code>AppException</code> 并派生出各种子类型报错。"
      },
      "app/application/services/app_config_service.py": {
        "title": "全局配置业务流程服务 (app_config_service.py)",
        "badge": "App Service",
        "desc": "负责处理全局配置的读取、修改、校验等业务逻辑的工作流。它通过调用 Domain 领域的接口定义，让配置能合规地读取和写入，并支持敏感数据（如 API Key）的安全掩码隐藏。",
        "analogy": "<b>全局游戏设置管理器 (GameSettingsManager)：</b> 类似你的 <code>GameSettingsManager</code> 脚本，负责具体控制游戏内设置读取与保存的『时机和权限』：比如修改画质时，它要先验证玩家是不是管理员账号，如果是，再调用物理磁盘组件写入。",
        "files": "使用 <code>AppConfigRepository</code> 仓储服务做存盘配合。"
      },
      "app/application/services/status_service.py": {
        "title": "系统状态诊断流程服务 (status_service.py)",
        "badge": "App Service",
        "desc": "系统健康判定工作流。它管理一组健康检查器（Postgres/Redis 等），当接到接口调用时，负责组织并发运行这一组检查器，聚合所有组件的连接状态，最终评估出服务的状态。",
        "analogy": "<b>系统自检协调器 (SystemDiagnosticManager)：</b> 类似于游戏启动时跑跑全自检：1. 检测内存是否够大；2. 检测网络 Socket 能不能连通；3. 检测本地显卡驱动支不支持。它负责组织这三项检测，如果某项失败，就通知流程失败。",
        "files": "支持注入一组实现了 <code>HealthChecker</code> 的检测实体对象进行并行校验。"
      },
      "app/domain/external/health_checker.py": {
        "title": "健康自检能力协议接口 (health_checker.py)",
        "badge": "Protocol Interface",
        "desc": "定义健康检查组件的 Protocol 契约，规定了任何检测器都必须具备 <code>check()</code> 方法，并返回 <code>HealthStatus</code> 模型。",
        "analogy": "<b>健康诊断组件接口 (IHealthCheckable)：</b> 类似 C# 中的 <code>public interface IHealthCheckable { Task<bool> Check(); }</code>，接口只写规范不写任何细节。只要是想成为诊断器的组件（比如检测帧率、检测内存等），都必须挂载并实现这个接口。",
        "files": "使用了 <code>Protocol</code> 进行强类型检查约束。"
      },
      "app/domain/external/llm.py": {
        "title": "LLM 核心大语言模型协议 (llm.py)",
        "badge": "Protocol Interface",
        "desc": "定义了 Agent 赖以生存的大语言模型调用契约，规范了必须提供 <code>chat()</code> 接口及各种上下文输入输出参数。",
        "analogy": "<b>聊天大模型交互接口 (ILLMClient)：</b> 类似于 Unity 里的 <code>public interface ILLMClient</code>。Agent 核心只需要调用这个接口去发消息、听回复，至于底层是用 ChatGPT 还是 DeepSeek，它不需要关心。只要实现了该接口的插件都能塞给它用。",
        "files": "核心定义了 <code>LLM</code> 能力 Protocol 类。"
      },
      "app/domain/external/message_queue.py": {
        "title": "核心消息队列协议 (message_queue.py)",
        "badge": "Protocol Interface",
        "desc": "定义了 Agent 并发时需要的数据同步队列以及分布式锁（Lock）的抽象功能规范，防止由于并发导致的状态错乱。",
        "analogy": "<b>网络同步队列与锁接口 (IMessageSyncQueue & ILock)：</b> 类似于在 Unity 多线程或联机同步中，为了防止两个玩家同时点开宝箱，我们需要一个排他锁接口和消息入栈队列接口，规范后续的线程互斥操作。",
        "files": "定义了包含 <code>publish</code>, <code>subscribe</code> 以及 <code>lock</code> 上下文管理器的 Protocol 规范。"
      },
      "app/domain/external/task.py": {
        "title": "后台任务运行器协议 (task.py)",
        "badge": "Protocol Interface",
        "desc": "规范了异步后台任务的执行容器协议，定义了如 `invoke()`（开始运行）、`cancel()`（打断取消）等基础行为。",
        "analogy": "<b>协程执行载体与管理器契约 (ICoroutineRunner)：</b> 类似于 Unity 中的 <code>MonoBehaviour</code>（有 StartCoroutine 协程管理能力）或者特殊的 Job 执行驱动接口。它只规定任务开始和中断取消的按钮，确保后台有条不紊地工作。",
        "files": "定义了 <code>Task</code> 状态接口类以及 <code>TaskRunner</code> 协程执行模型。"
      },
      "app/domain/external/json_parser.py": {
        "title": "JSON 解析与自动纠偏协议 (json_parser.py)",
        "badge": "Protocol Interface",
        "desc": "定义了解析大模型 JSON 字符串的 Protocol 协议。核心契约是 `invoke(text, default_value)`，保证在传入破损的文本时，具备容错返回与修复的机制。",
        "analogy": "<b>不完整数据读取接口 (IDamagedJSONReader)：</b> 类似于 Unity 里定义的一个辅助文件解析接口。它只规定在读不完整存档时，如何自动补足缺失括号并安全反序列化成 C# 类的协议契约。",
        "files": "使用了 Protocol 进行强类型契约声明。"
      },
      "app/domain/models/app_config.py": {
        "title": "系统全局配置领域实体 (app_config.py)",
        "badge": "Domain Model",
        "desc": "定义了 MoocManus 全局系统级的强类型实体数据。包含了 LLM 的各项配置，并带有敏感数据（如 API Key）掩码遮罩的核心计算逻辑。",
        "analogy": "<b>全局属性核心结构体 (GameConfigEntity)：</b> 类似你的纯 C# 属性类 <code>public class GameConfig</code>，它包含了服务器 IP、用户名等，并提供比如 <code>GetMaskedKey()</code> 这样的逻辑运算。它是不需要 MonoBehaviour 的纯粹数据体。",
        "files": "基于 Pydantic <code>BaseModel</code> 定义，包含 <code>AppConfig</code> 实体与 <code>LLMConfig</code> 配置类。"
      },
      "app/domain/models/event.py": {
        "title": "多态事件流领域模型 (event.py)",
        "badge": "Domain Model",
        "desc": "定义了 Agent 运行过程中产生的一切日志、行为、工具执行事件流。使用了辨别器（Discriminator）机制，可以在单条 JSON 报文中根据 `type` 类型字段，智能拆箱为具体的子类事件。",
        "analogy": "<b>游戏行为多态事件 (GameEvent 多态派生)：</b> 类似于你游戏的网络事件类。一个基类 <code>GameEvent</code> 派生出 <code>ChatMessageEvent</code>、<code>FileCreatedEvent</code>、<code>ToolExecutedEvent</code>。通过 Type 字段自动 `switch` 转型到最精准的子类去解析处理。",
        "files": "基于 Pydantic <code>Field(discriminator='type')</code> 高效支持多态数据验证。"
      },
      "app/domain/models/file.py": {
        "title": "物理文件记录领域模型 (file.py)",
        "badge": "Domain Model",
        "desc": "定义了 Manus 上传、生成、读取的物理文件的全部元数据：包括大小、MIME 类型、云存储路径 COS 键以及本地物理路径。",
        "analogy": "<b>文件资产数据实体 (AssetFileEntity)：</b> 类似于你游戏内定义的一个纯逻辑文件描述类。无论这个关卡地图文件存放在本地电脑，还是存放在 CDN 远程服务器，这一层都用统一的属性来代表它，便于大模型分析。",
        "files": "内含文件名、相对/绝对路径、文件大小字节等属性字段。"
      },
      "app/domain/models/health_status.py": {
        "title": "健康度状态评估领域模型 (health_status.py)",
        "badge": "Domain Model",
        "desc": "定义了诊断后得到的系统状态数据格式（包含组件名、是否在线、耗时、异常原因等）。",
        "analogy": "<b>性能诊断状态实体 (SystemStatusReport)：</b> 用于保存帧率、内存、连接耗时等检测结果的纯数据存储包格式。",
        "files": "Pydantic 对象模型。"
      },
      "app/domain/models/memory.py": {
        "title": "记忆与上下文自动压缩领域模型 (memory.py)",
        "badge": "Domain Model",
        "desc": "定义了 Agent 专用的长期/短期记忆体。这里包含了一项高级压缩逻辑（`compact`）：如果检测到历史上下文中包含巨幅的 HTML 网页源码，它会自动将其中的大段标签替换为极简标签，从而在推理大模型时大幅节约 Token 消耗，防止内存爆满。",
        "analogy": "<b>聊天缓存与其内存清理机制 (ChatHistory & GarbageCollector)：</b> 类似你的游戏聊天面板数据缓存。当聊天消息存了超过 1000 条，或者某条消息体积过大时，核心逻辑会启动压缩（比如清除富文本标签），确保不会撑爆内存引发 OOM 闪退。",
        "files": "提供 <code>compact()</code> 记忆体压缩核心算法逻辑。"
      },
      "app/domain/models/plan.py": {
        "title": "主任务步骤计划控制模型 (plan.py)",
        "badge": "Domain Model",
        "desc": "定义了 Agent 拆解复杂任务时的计划树。每一个 <code>Plan</code> 由多条 <code>Step</code> 组成，包含自动按顺序获取『下一条待执行任务』的 `get_next_step` 算法逻辑，充当了任务状态机的核心流转规则。",
        "analogy": "<b>主线任务步骤控制器 (QuestTreeController)：</b> 类似于你的 RPG 游戏任务树。主任务下有子步骤：1. 对话 NPC；2. 杀五只野狼；3. 复命。该脚本负责追踪每一项是否完成（TODO/DONE），并在被呼叫时准确给出当前哪一步才需要被执行。",
        "files": "包含了 <code>Step</code> 模型及 <code>Plan</code> 控制类的属性与实现方法。"
      },
      "app/domain/models/search.py": {
        "title": "网络检索状态实体 (search.py)",
        "badge": "Domain Model",
        "desc": "定义了 Agent 网络搜索的元数据（包含查询词、标题、网址链接、摘要、发布时间）。",
        "analogy": "<b>检索数据类 (SearchItemEntity)：</b> 用来规范每次通过爬虫从网络上获取的内容的格式包，以便大模型解析。",
        "files": "Pydantic 属性模型。"
      },
      "app/domain/models/tool_result.py": {
        "title": "工具运行结果领域实体 (tool_result.py)",
        "badge": "Domain Model",
        "desc": "定义了 Agent 调用沙箱工具（如执行 Python 代码、运行命令行）后返回的结果包体（包括退出状态码、是否成功、错误输出）。",
        "analogy": "<b>物理进程执行结果包 (CommandLineResultEntity)：</b> 类似于你在游戏内利用 C# `Process` 执行本地命令行后拿到的返回包：包含 `ErrorCode` 以及控制台的红字日志，给上层的决策类看。",
        "files": "定义了 tool 结果的元数据格式。"
      },
      "app/domain/repositories/app_config_repository.py": {
        "title": "全局配置仓储抽象接口 (app_config_repository.py)",
        "badge": "Repository Interface",
        "desc": "定义配置存储读写的 ISaveLoader 接口。只写出了 `get()` 和 `save()` 的函数契约声明，不依赖具体的文件或数据库读写逻辑。",
        "analogy": "<b>数据存档接口 (ISettingsSaveLoader)：</b> 声明用于保存全局画质、音量等配置的接口。具体怎么写盘它不管，由实现该接口的类在基础设施层具体做。",
        "files": "定义了 <code>AppConfigRepository</code> 抽象接口类。"
      },
      "app/infrastructure/external/health_checker/postgres_health_checker.py": {
        "title": "Postgres 数据库健康自检实现 (postgres_health_checker.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>HealthChecker</code> 接口。在内部具体去对物理 Postgres 数据库发起一次 <code>SELECT 1</code> 查询，如果连通且超时在允许范围内，即返回 ok，否则报告连接失败。",
        "analogy": "<b>SQL 数据库物理连接判定器：</b> 类似于你写了一个真实判定 SQL 是否连通的脚本。一旦运行，它向 SQL 服务发命令，如果没响应直接向系统抛出红字报告。",
        "files": "依赖 SQLAlchemy 的异步 session连接进行检查。"
      },
      "app/infrastructure/external/health_checker/redis_health_checker.py": {
        "title": "Redis 缓存健康自检实现 (redis_health_checker.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>HealthChecker</code> 接口。向真实的 Redis 服务器发送一条 <code>PING</code> 命令，判定是否有 pong 返回，从而确定缓存系统是否瘫痪。",
        "analogy": "<b>Redis 物理连接判定器：</b> 类似于你游戏自检时发起对局域网 Redis 服务的网络 Ping 检测，PING 没通则宣告联机自检失败。",
        "files": "使用 <code>redis_client.client.ping()</code> 执行校验。"
      },
      "app/infrastructure/external/llm/openaillm.py": {
        "title": "大语言模型网络通信实现类 (openaillm.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>LLM</code> 接口。通过 HTTP 网络通道，真正去向外网的 OpenAI / DeepSeek 服务器发起 POST 请求，提交当前的聊天记忆列表，并接收处理大模型的流式或同步返回。",
        "analogy": "<b>大模型网络请求通信类 (ILLMClient 实现)：</b> 类似于你在 Unity 中具体写 <code>UnityWebRequest</code> 把聊天字串序列化发给 DeepSeek 接口，并在收到 JSON 返回包时解析出大模型的回答文本。",
        "files": "使用异步网络请求，根据传入参数执行 chat 通信操作。"
      },
      "app/infrastructure/external/message_queue/redis_stream_message_queue.py": {
        "title": "Redis Stream 消息队列与分布式锁实现 (redis_stream_message_queue.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>MessageQueue</code> 接口。利用 Redis 的 Stream 数据类型真正地进行消息发布（xadd）、监听订阅（xreadgroup）并支持在多进程并发时利用 Redis 的 key 互斥特性来加锁。",
        "analogy": "<b>基于 Redis 物理连接的高性能局域网同步广播器：</b> 类似于你在 Unity 联机开发中，为了同步多个玩家在各自手机上的操作状态，接入的真实的基于网络的数据分发中转件，它负责物理网包的进栈出栈和防冲突多线程锁机制。",
        "files": "实现了一整套 Redis Distributed Lock 分布式排他锁机制。"
      },
      "app/infrastructure/external/task/redis_stream_task.py": {
        "title": "Redis Stream 后台任务驱动类 (redis_stream_task.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>Task</code> 接口。将任务发送给 Redis 队列，并且在后台开启一个 asyncio 的非阻塞监听器，监听到任务后通过 <code>asyncio.create_task</code> 在独立的物理协程里去 safe 跑起来。",
        "analogy": "<b>异步协程工作线程管理器 (TaskCoroutineDriver)：</b> 类似于你在 Unity 中写了一个专门管理所有正在跑的 Coroutine 的后台管理器：它可以动态 <code>StartCoroutine</code>，并且如果某协程卡死，它能远程将其强行 Cancel 打断并清理场景垃圾。",
        "files": "配合 Redis 消息发布与订阅实现非阻塞的任务调度系统。"
      },
      "app/infrastructure/external/json_parser/repair_json_parser.py": {
        "title": "JSON 自动修复解析器 (repair_json_parser.py)",
        "badge": "Infra Realization",
        "desc": "具体实现 domain 层的 <code>JSONParser</code> 接口。专门使用第三方 <code>json_repair</code> 库将损坏了大括号、有多余标记的不规范大模型 JSON 文本自动还原纠错，并直接反序列化为 Python 对象。",
        "analogy": "<b>容错反序列化读写器 (ILLMJsonReader 实现)：</b> 类似于你写的一个增强型 JsonUtility。如果从云端读进来的 JSON 数据格式坏了（比如结尾缺了半边花括号 `}`），它能自动给你补上，并成功 `FromJson<T>` 返回类对象而不断言崩溃。",
        "files": "使用 <code>return_objects=True</code> 来实现物理纠错并直接转为 dict / list。"
      },
      "app/infrastructure/logging/logging.py": {
        "title": "系统日志全局初始化 (logging.py)",
        "badge": "Infra Logging",
        "desc": "负责后端日志系统的底色初始化。配置日志级别（如 INFO/DEBUG）、输出格式（时间、调用行号、线程名）以及具体输出的目的地（控制台输出）。",
        "analogy": "<b>Unity Debug.Log 控制器：</b> 类似你自定义的 <code>GameLogger</code>，控制在 Play 模式和打包（Build）后哪些日志可以打印在 Console 界面，哪些日志需要存入本地的 <code>output_log.txt</code> 文件中。",
        "files": "定义了终端日志记录规范。"
      },
      "app/infrastructure/models/base.py": {
        "title": "物理数据库元数据基类 (base.py)",
        "badge": "DB Base Meta",
        "desc": "SQLAlchemy ORM 数据库模型的声明基类（Declarative Base）。在这里注册所有的物理表元数据，给 Alembic 数据库升级工具读取以判定字段有何差异。",
        "analogy": "<b>数据库物理映射基类：</b> 类似于你使用物理 SQLite 存档时的表基类，保存物理数据表的最底层的结构元信息，所有的表实体（如 PlayerTable, ItemTable）都继承于它。",
        "files": "所有 app.infrastructure.models 包下的模型都需继承于它。"
      },
      "app/infrastructure/models/demo.py": {
        "title": "SQL 物理测试演示表映射类 (demo.py)",
        "badge": "DB Entity Table",
        "desc": "定义了一个真实的 PostgreSQL 物理测试表。包含 email、ID 等字段，展示 SQLAlchemy 怎么把 Python 类直接转换成数据库里实打实的行和列。",
        "analogy": "<b>物理存档表数据结构 (Table Row Entity)：</b> 类似于你物理数据库里存放玩家名册的数据行实体类：<code>public class PlayerInfoRow { public string Id; public string Email; }</code>。",
        "files": "对应真实的数据库物理表 <code>users</code>。"
      },
      "app/infrastructure/repositories/file_app_config_repository.py": {
        "title": "配置本磁盘 YAML 仓储实现 (file_app_config_repository.py)",
        "badge": "Infra Realization",
        "desc": "具体继承并实现了 domain 层的 <code>AppConfigRepository</code> 接口。利用 `ruamel.yaml` 第三方库，写出具体的物理读盘、写盘行为，把系统的全局大模型配置，持久化写入本地的 <code>config.yaml</code> 磁盘文件。",
        "analogy": "<b>本地磁盘 YAML 存盘插件 (LocalYAMLWriter)：</b> 类似于你写的一个物理读取脚本。当你要求 ISaveLoader保存设置时，它负责在手机后台用 C# 将配置类转成 YAML 字符串并安全地写入 <code>Application.persistentDataPath + '/config.yaml'</code> 中。",
        "files": "在 `save` 方法中完成了敏感 API_KEY 掩码的比对并安全写盘。"
      },
      "app/infrastructure/storage/cos.py": {
        "title": "腾讯云对象存储 COS 初始化 (cos.py)",
        "badge": "Cloud Storage",
        "desc": "负责连接腾讯云 COS 对象存储。根据环境变量中的 secret_id、secret_key、bucket 名，初始化并托管云存储的 Python 客户端。",
        "analogy": "<b>远程资源同步 SDK (OSS/COS Downloader)：</b> 类似于你在 Unity 里接入的第三方阿里云/腾讯云 CDN 上传下载 SDK 引导器。通过鉴权密匙建立好连接，随时准备将游戏里的玩家截图、存档同步到远程的云端 Bucket 里。",
        "files": "提供云对象存储的物理连接方法。"
      },
      "app/infrastructure/storage/postgres.py": {
        "title": "SQL 物理连接与异步会话池 (postgres.py)",
        "badge": "PostgreSQL Session",
        "desc": "管理 PostgreSQL 关系数据库的物理连接。使用 asyncpg 异步驱动器建立数据库引擎（Engine），并配置异步会话池工厂（sessionmaker），供外部随时申请和归还连接通道。",
        "analogy": "<b>SQL 异步连接池管理器 (SqlConnectionPool)：</b> 类似于游戏服务器上统一管物理 SQL 数据库连接的管理器。它预先分配好 10 条连接通道供客户端异步存取数据，防止频繁开闭连接通道造成的资源耗尽故障。",
        "files": "定义了 <code>get_db_session()</code> 生成器依赖供请求流调用。"
      },
      "app/infrastructure/storage/redis.py": {
        "title": "缓存数据库 Redis 连接器 (redis.py)",
        "badge": "Redis client",
        "desc": "管理物理 Redis 缓存连接。负责在服务启动时建立连接池，托管 Redis 的异步网络客户端（RedisClient），以进行高并发状态存储 and 分布式加锁操作。",
        "analogy": "<b>内存数据库连接器：</b> 类似你在游戏开发中用来连接极速内存数据库 Redis 的连接助手。它确保你的 Agent 在推理循环中能以接近零毫秒延迟的速度从内存里读取短期任务状态。",
        "files": "管理 Redis 连接的初始化与 `client` 的导出。"
      }
}

# 终极 HTML 静态模版
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MoocManus 架构目录导航与 Unity 开发类比导览</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --bg-gradient: linear-gradient(135deg, #0f172a 0%, #020617 100%);
      --card-bg: rgba(30, 41, 59, 0.45);
      --card-border: rgba(255, 255, 255, 0.08);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      
      --blue-gradient: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
      --blue-glow: rgba(59, 130, 246, 0.35);
      --green-gradient: linear-gradient(135deg, #10b981 0%, #047857 100%);
      --green-glow: rgba(16, 185, 129, 0.35);
      --purple-gradient: linear-gradient(135deg, #8b5cf6 0%, #5b21b6 100%);
      --purple-glow: rgba(139, 92, 246, 0.35);
      --orange-gradient: linear-gradient(135deg, #f97316 0%, #c2410c 100%);
      --orange-glow: rgba(249, 115, 22, 0.35);
      
      --accent-color: #a855f7;
      --accent-glow: rgba(168, 85, 247, 0.4);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background: var(--bg-gradient);
      color: var(--text-main);
      font-family: 'Outfit', 'Inter', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding: 2.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    header {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      padding: 1.5rem 2rem;
      border-radius: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
    }

    .header-title h1 {
      font-size: 1.8rem;
      font-weight: 700;
      background: linear-gradient(90deg, #a855f7 0%, #3b82f6 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 0.2rem;
    }

    .header-title p {
      color: var(--text-muted);
      font-size: 0.9rem;
    }

    .controls {
      display: flex;
      gap: 0.8rem;
      align-items: center;
    }

    input[type="text"] {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border);
      padding: 0.6rem 1rem;
      border-radius: 8px;
      color: var(--text-main);
      font-family: 'Inter', sans-serif;
      font-size: 0.9rem;
      outline: none;
      width: 250px;
      transition: all 0.3s ease;
    }

    input[type="text"]:focus {
      border-color: var(--accent-color);
      box-shadow: 0 0 10px var(--accent-glow);
    }

    button.btn {
      background: rgba(168, 85, 247, 0.15);
      border: 1px solid rgba(168, 85, 247, 0.3);
      color: #e9d5ff;
      padding: 0.6rem 1.2rem;
      border-radius: 8px;
      font-weight: 500;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s ease;
    }

    button.btn:hover {
      background: var(--accent-color);
      color: #fff;
      box-shadow: 0 0 15px var(--accent-glow);
      transform: translateY(-1px);
    }

    .main-container {
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 1.5rem;
      flex-grow: 1;
    }

    .panel {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-radius: 16px;
      padding: 2rem;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      display: flex;
      flex-direction: column;
      height: 780px;
    }

    .panel-title {
      font-size: 1.3rem;
      font-weight: 600;
      margin-bottom: 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      padding-bottom: 0.8rem;
    }

    .tree-scroll-area {
      flex-grow: 1;
      overflow-y: auto;
      padding-right: 0.5rem;
    }

    ::-webkit-scrollbar {
      width: 6px;
    }
    ::-webkit-scrollbar-track {
      background: rgba(0,0,0,0.1);
      border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,0.15);
      border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255,255,255,0.3);
    }

    .tree-list {
      list-style: none;
      padding-left: 1.2rem;
      position: relative;
    }

    .tree-list::before {
      content: '';
      position: absolute;
      left: 6px;
      top: 0;
      bottom: 0;
      width: 1px;
      background: rgba(255, 255, 255, 0.07);
    }

    .root-tree > .tree-list::before {
      display: none;
    }
    .root-tree > .tree-list {
      padding-left: 0;
    }

    .tree-item {
      margin: 0.4rem 0;
      position: relative;
    }

    .tree-item::before {
      content: '';
      position: absolute;
      left: -13px;
      top: 12px;
      width: 10px;
      height: 1px;
      background: rgba(255, 255, 255, 0.07);
    }

    .root-tree .tree-item::before {
      display: none;
    }

    .tree-row {
      display: flex;
      align-items: center;
      gap: 0.6rem;
      padding: 0.4rem 0.6rem;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.2s ease;
      user-select: none;
    }

    .tree-row:hover {
      background: rgba(255, 255, 255, 0.04);
    }

    .tree-row.active-row {
      background: rgba(168, 85, 247, 0.1);
      border-left: 3px solid var(--accent-color);
      padding-left: calc(0.6rem - 3px);
    }

    .toggle-icon {
      font-size: 0.8rem;
      width: 14px;
      text-align: center;
      color: var(--text-muted);
      transition: transform 0.2s ease;
    }

    .toggle-icon.open {
      transform: rotate(90deg);
    }

    .node-icon {
      font-size: 1.1rem;
    }

    .node-name {
      font-weight: 500;
      color: var(--text-main);
      font-size: 0.95rem;
    }

    .node-comment {
      color: var(--text-muted);
      font-size: 0.85rem;
      margin-left: auto;
      font-family: 'Inter', sans-serif;
      padding-left: 1rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 50%;
    }

    .badge {
      font-size: 0.75rem;
      padding: 0.2rem 0.5rem;
      border-radius: 4px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #fff;
    }

    .badge-interfaces {
      background: var(--blue-gradient);
      box-shadow: 0 0 8px var(--blue-glow);
    }

    .badge-application {
      background: var(--green-gradient);
      box-shadow: 0 0 8px var(--green-glow);
    }

    .badge-domain {
      background: var(--purple-gradient);
      box-shadow: 0 0 8px var(--purple-glow);
    }

    .badge-infrastructure {
      background: var(--orange-gradient);
      box-shadow: 0 0 8px var(--orange-glow);
    }

    .row-interfaces { border-right: 3px solid #3b82f6; }
    .row-application { border-right: 3px solid #10b981; }
    .row-domain { border-right: 3px solid #8b5cf6; }
    .row-infrastructure { border-right: 3px solid #f97316; }

    .detail-panel {
      overflow-y: auto;
    }

    .welcome-view {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      text-align: center;
      height: 100%;
      color: var(--text-muted);
      gap: 1rem;
    }

    .welcome-view svg {
      width: 64px;
      height: 64px;
      stroke: var(--text-muted);
      opacity: 0.5;
    }

    .detail-content {
      display: flex;
      flex-direction: column;
      gap: 1.2rem;
      animation: fadeIn 0.25s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .detail-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .detail-header h2 {
      font-size: 1.5rem;
      font-weight: 700;
    }

    .card-block {
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 1.2rem;
    }

    .card-block-title {
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 0.6rem;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      color: #e2e8f0;
    }

    .card-block-title svg {
      width: 18px;
      height: 18px;
    }

    .card-block p {
      font-size: 0.92rem;
      color: #cbd5e1;
      line-height: 1.6;
    }

    .unity-analogy-card {
      background: linear-gradient(135deg, rgba(234, 179, 8, 0.07) 0%, rgba(249, 115, 22, 0.07) 100%);
      border: 1px solid rgba(234, 179, 8, 0.25);
      position: relative;
    }

    .unity-analogy-card::after {
      content: 'UNITY ANALOGY';
      position: absolute;
      top: -9px;
      right: 12px;
      background: #eab308;
      color: #0f172a;
      font-size: 0.65rem;
      font-weight: 800;
      padding: 1px 6px;
      border-radius: 4px;
      letter-spacing: 0.8px;
    }

    .unity-analogy-card .card-block-title {
      color: #fef08a;
    }

    code {
      background: rgba(0, 0, 0, 0.3);
      padding: 0.15rem 0.4rem;
      border-radius: 4px;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.85rem;
      color: #f472b6;
    }

    .hidden {
      display: none !important;
    }
  </style>
</head>
<body>

  <header>
    <div class="header-title">
      <h1>MoocManus 架构目录导航</h1>
      <p>面向 Unity 开发转 Python / Agent 全栈开发者的干净架构图解</p>
    </div>
    <div class="controls">
      <input type="text" id="search-input" placeholder="输入名称或注释检索..." oninput="filterTree()">
      <button class="btn" onclick="expandAll()">展开全部</button>
      <button class="btn" onclick="collapseAll()">折叠全部</button>
    </div>
  </header>

  <div class="main-container">
    <div class="panel">
      <div class="panel-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent-color);"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
        代码项目物理目录树
      </div>
      <div class="tree-scroll-area" id="tree-container">
        <!-- 树结构通过 JS 渲染 -->
      </div>
    </div>

    <div class="panel detail-panel" id="detail-panel">
      <div class="welcome-view" id="welcome-view">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <p>点击左侧的<b>任何文件夹或具体文件</b>，在此查看微观的作用解析与 Unity 开发对应类比。</p>
      </div>
      <div class="detail-content hidden" id="detail-content">
        <!-- 内容由 JS 动态装载 -->
      </div>
    </div>
  </div>

  <script>
    const treeData = {tree_data_placeholder};
    const nodeDetails = {node_details_placeholder};

    function buildTreeHTML(node, isRoot = false) {
      let html = '';
      const hasChildren = node.children && node.children.length > 0;
      
      let layerClass = '';
      let badgeHTML = '';
      if (node.layer) {
        layerClass = `row-${node.layer}`;
        badgeHTML = `<span class="badge badge-${node.layer}">${node.layer}</span>`;
      }

      html += `<li class="tree-item" data-name="${node.name.toLowerCase()}" data-comment="${node.comment.toLowerCase()}">`;
      html += `  <div class="tree-row ${layerClass}" onclick="handleNodeClick(event, this, '${node.layer || ''}', '${node.name}')">`;
      
      if (hasChildren) {
        const isOpen = node.isOpen ? 'open' : '';
        html += `    <span class="toggle-icon ${isOpen}">▶</span>`;
      } else {
        html += `    <span class="toggle-icon" style="opacity: 0;">▶</span>`;
      }

      const icon = node.type === 'folder' ? '📁' : '📄';
      html += `    <span class="node-icon">${icon}</span>`;
      html += `    <span class="node-name">${node.name}</span>`;
      if (badgeHTML) html += `    ${badgeHTML}`;
      html += `    <span class="node-comment">${node.comment}</span>`;
      html += `  </div>`;

      if (hasChildren) {
        const displayStyle = node.isOpen ? '' : 'style="display: none;"';
        html += `  <ul class="tree-list" ${displayStyle}>`;
        node.children.forEach(child => {
          html += buildTreeHTML(child);
        });
        html += `  </ul>`;
      }
      
      html += `</li>`;
      return html;
    }

    const treeContainer = document.getElementById('tree-container');
    treeContainer.innerHTML = `<div class="root-tree"><ul class="tree-list">${buildTreeHTML(treeData, true)}</ul></div>`;

    function handleNodeClick(event, element, layerName, nodeName) {
      event.stopPropagation();
      
      document.querySelectorAll('.tree-row').forEach(row => row.classList.remove('active-row'));
      element.classList.add('active-row');

      const li = element.parentElement;
      const subList = li.querySelector('.tree-list');
      const toggleIcon = element.querySelector('.toggle-icon');
      
      if (subList) {
        if (subList.style.display === 'none') {
          subList.style.display = '';
          if (toggleIcon) toggleIcon.classList.add('open');
        } else {
          if (event.target.classList.contains('toggle-icon') || (!layerName && !nodeDetails[nodeName])) {
            subList.style.display = 'none';
            if (toggleIcon) toggleIcon.classList.remove('open');
          }
        }
      }

      const relativePath = getRelativePath(element);

      if (nodeDetails[relativePath]) {
        showDetails(relativePath);
      } else if (nodeDetails[nodeName]) {
        showDetails(nodeName);
      } else if (layerName && nodeDetails[layerName]) {
        showDetails(layerName);
      } else {
        const comment = element.querySelector('.node-comment').innerText;
        showGenericDetails(nodeName, comment);
      }
    }

    function getRelativePath(element) {
      const pathParts = [];
      let currentLi = element.parentElement;
      while (currentLi && currentLi.classList.contains('tree-item')) {
        const row = currentLi.querySelector('.tree-row');
        const name = row.querySelector('.node-name').innerText;
        if (!name.includes("mooc-manus (项目根目录)")) {
          pathParts.unshift(name);
        }
        currentLi = currentLi.parentElement.parentElement;
      }
      return pathParts.join('/');
    }

    function showDetails(nodeKey) {
      const data = nodeDetails[nodeKey];
      const welcomeView = document.getElementById('welcome-view');
      const detailContent = document.getElementById('detail-content');
      
      welcomeView.classList.add('hidden');
      detailContent.classList.remove('hidden');

      let badgeStyle = "background: var(--accent-color); box-shadow: 0 0 8px var(--accent-glow);";
      const lowerKey = nodeKey.toLowerCase();
      if (lowerKey.includes('interfaces')) badgeStyle = "background: var(--blue-gradient); box-shadow: 0 0 8px var(--blue-glow);";
      else if (lowerKey.includes('application')) badgeStyle = "background: var(--green-gradient); box-shadow: 0 0 8px var(--green-glow);";
      else if (lowerKey.includes('domain')) badgeStyle = "background: var(--purple-gradient); box-shadow: 0 0 8px var(--purple-glow);";
      else if (lowerKey.includes('infrastructure')) badgeStyle = "background: var(--orange-gradient); box-shadow: 0 0 8px var(--orange-glow);";

      detailContent.innerHTML = `
        <div class="detail-header">
          <h2>${data.title}</h2>
          <span class="badge" style="${badgeStyle}">${data.badge}</span>
        </div>
        
        <div class="card-block">
          <div class="card-block-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            组件职责与定位说明
          </div>
          <p>${data.desc}</p>
        </div>

        <div class="card-block unity-analogy-card">
          <div class="card-block-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            Unity 开发视角类比 🎮
          </div>
          <p>${data.analogy}</p>
        </div>

        <div class="card-block">
          <div class="card-block-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            项目代表文件与技术
          </div>
          <p>${data.files}</p>
        </div>
      `;
    }

    function showGenericDetails(name, comment) {
      const welcomeView = document.getElementById('welcome-view');
      const detailContent = document.getElementById('detail-content');
      
      welcomeView.classList.add('hidden');
      detailContent.classList.remove('hidden');

      detailContent.innerHTML = `
        <div class="detail-header">
          <h2>${name}</h2>
          <span class="badge" style="background: var(--accent-color); box-shadow: 0 0 8px var(--accent-glow);">DETAIL</span>
        </div>
        
        <div class="card-block">
          <div class="card-block-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            作用说明
          </div>
          <p>${comment || '该文件/文件夹是项目中的辅助逻辑模块，负责提供底层的细节支撑。'}</p>
        </div>

        <div class="card-block unity-analogy-card">
          <div class="card-block-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            Unity 开发视角类比 🎮
          </div>
          <p>类似于你游戏项目目录下的辅助资源文件、特定模块工具类（Utility Class）或单项功能脚本，负责配合大层级提供局部的细节逻辑支持。</p>
        </div>
      `;
    }

    function expandAll() {
      document.querySelectorAll('.tree-list').forEach(list => {
        list.style.display = '';
      });
      document.querySelectorAll('.toggle-icon').forEach(icon => {
        if (icon.style.opacity !== '0') {
          icon.classList.add('open');
        }
      });
    }

    function collapseAll() {
      const rootList = document.querySelector('.root-tree > .tree-list');
      document.querySelectorAll('.tree-list').forEach(list => {
        if (list !== rootList) {
          list.style.display = 'none';
        }
      });
      document.querySelectorAll('.toggle-icon').forEach(icon => {
        const parentList = icon.closest('.tree-list');
        if (parentList !== rootList) {
          icon.classList.remove('open');
        }
      });
    }

    function filterTree() {
      const query = document.getElementById('search-input').value.toLowerCase().trim();
      const items = document.querySelectorAll('.tree-item');
      
      if (!query) {
        items.forEach(item => item.classList.remove('hidden'));
        return;
      }

      items.forEach(item => {
        const name = item.getAttribute('data-name');
        const comment = item.getAttribute('data-comment');
        
        if (name.includes(query) || comment.includes(query)) {
          item.classList.remove('hidden');
          
          let parent = item.parentElement;
          while (parent && parent.classList.contains('tree-list')) {
            parent.style.display = '';
            const parentRow = parent.previousElementSibling;
            if (parentRow) {
              const icon = parentRow.querySelector('.toggle-icon');
              if (icon) icon.classList.add('open');
            }
            parent = parent.parentElement.parentElement;
          }
        } else {
          item.classList.add('hidden');
        }
      });

      items.forEach(item => {
        const subList = item.querySelector('.tree-list');
        if (subList) {
          const visibleChildren = subList.querySelectorAll('.tree-item:not(.hidden)');
          if (visibleChildren.length > 0) {
            item.classList.remove('hidden');
          }
        }
      });
    }
  </script>
</body>
</html>
"""

def build_tree_data(path, name):
    is_dir = os.path.isdir(path)
    rel_path = os.path.relpath(path, PROJECT_ROOT).replace("\\", "/")
    
    if is_dir:
        base = os.path.basename(path)
        if base in (".git", ".venv", "__pycache__", ".idea", ".agents", "scratch", "tmp", "docs") or "egg-info" in base:
            return None
            
    layer = None
    for prefix, ly in LAYERS.items():
        if rel_path.startswith(prefix):
            layer = ly
            break
            
    comment = ""
    if rel_path in STATIC_DETAILS:
        comment = STATIC_DETAILS[rel_path]["desc"]
    elif os.path.basename(path) in STATIC_DETAILS:
        comment = STATIC_DETAILS[os.path.basename(path)]["desc"]
    else:
        if os.path.basename(path) == "__init__.py":
            comment = "Python 包初始化入口（类似 Unity 里的命名空间导入绑定声明）"
        elif is_dir:
            comment = f"【目录】存放 {os.path.basename(path)} 的相关代码模块"
        else:
            comment = f"【文件】提供 {os.path.basename(path)} 支持的辅助脚本"

    node = {
        "name": name,
        "type": "folder" if is_dir else "file",
        "comment": comment,
        "isOpen": True if is_dir and rel_path in (".", "app") else False
    }
    
    if layer:
        node["layer"] = layer
        
    if is_dir:
        children = []
        try:
            for item in sorted(os.listdir(path)):
                child_path = os.path.join(path, item)
                child_node = build_tree_data(child_path, item)
                if child_node:
                    children.append(child_node)
        except Exception as e:
            pass
        node["children"] = children
        
    return node

def get_micro_details(path):
    details = {}
    
    for key, val in STATIC_DETAILS.items():
        details[key] = val
        
    def walk_dir(current_path):
        base = os.path.basename(current_path)
        if base in (".git", ".venv", "__pycache__", ".idea", ".agents", "scratch", "tmp", "docs") or "egg-info" in base:
            return
            
        rel_path = os.path.relpath(current_path, PROJECT_ROOT).replace("\\", "/")
        
        layer_name = None
        for prefix, ly in LAYERS.items():
            if rel_path.startswith(prefix):
                layer_name = ly
                break

        if rel_path not in details and base not in details:
            is_dir = os.path.isdir(current_path)
            
            if base == "__init__.py":
                details[rel_path] = {
                    "title": f"包初始化文件 ({base})",
                    "badge": "Package Init",
                    "desc": f"Python 语言的规范设计。用于将当前文件夹（<code>{os.path.dirname(rel_path)}</code>）标识为一个 Python 包，使得该目录下的各个模块能被外部通过 <code>import</code> 关键字正常加载。",
                    "analogy": "<b>命名空间声明 (Namespace Registration)：</b> 类似于在 Unity/C# 中，通过在脚本头部声明 <code>namespace MyGame.App { ... }</code> 将一堆分散的脚本文件绑定在同一个逻辑命名空间下，方便跨模块引用。",
                    "files": "代表包：<code>" + os.path.dirname(rel_path).replace("/", ".") + "</code>。"
                }
            elif is_dir:
                badge = "Folder / Module"
                desc = f"存放 {base} 功能模块的源代码目录。"
                analogy = f"<b>Unity 子模块资源目录：</b> 类似于你 Assets/Scripts 下为 {base} 专属开辟的资源目录，用于收纳其所有相关的辅助脚本和数据预制体。"
                if layer_name:
                    badge = f"{layer_name} Subfolder"
                    desc = f"隶属于【{layer_name}】层的 {base} 子业务模块目录。"
                    
                details[rel_path] = {
                    "title": f"{base} 功能目录",
                    "badge": badge,
                    "desc": desc,
                    "analogy": analogy,
                    "files": "包含该模块下的各个业务 Python 实现代码。"
                }
            else:
                badge = "Python Script"
                desc = f"提供 {base} 局部辅助能力的 Python 代码文件。"
                analogy = f"<b>辅助功能脚本：</b> 类似于挂载在游戏场景局部的 MonoBehaviour 组件或特定的静态 Utility 算法类，为 {base} 的总调用提供局部计算支撑。"
                
                if rel_path.startswith("tests/"):
                    badge = "Test Script"
                    desc = f"针对系统业务功能编写的自动化单元测试用例脚本 ── <code>{base}</code>。"
                    analogy = "<b>Editor 自动化单元测试类 (PlayMode Test Suite)：</b> 类似于在 Unity Test Runner 框架下专门为验证某特定机制（如玩家血量扣减是否正确）而编写的断言测试脚本。"
                elif "/models/" in rel_path:
                    badge = "Domain Model"
                    desc = f"Agent 领域内用于表示 <code>{base.replace('.py','')}</code> 数据结构的核心模型实体类。"
                    analogy = "<b>纯数值核心实体类 (Pure C# Class)：</b> 类似你的游戏内定义的一个纯数据结构类（如 <code>class MonsterAttr { public float speed; }</code>），专门在运行时作为大模型思考和决策的轻量数据载体。"
                
                details[rel_path] = {
                    "title": f"{base} 脚本文件",
                    "badge": badge,
                    "desc": desc,
                    "analogy": analogy,
                    "files": f"包含的具体代码文件路径为：<code>{rel_path}</code>。"
                }

        if os.path.isdir(current_path):
            for item in os.listdir(current_path):
                walk_dir(os.path.join(current_path, item))
                
    walk_dir(PROJECT_ROOT)
    return details

def main():
    print("开始全量物理扫描...")
    root_node = build_tree_data(PROJECT_ROOT, "mooc-manus (项目根目录)")
    details = get_micro_details(PROJECT_ROOT)
    
    print(f"扫描完成，共有 {len(details)} 个物理节点数据。")
    
    tree_data_str = json.dumps(root_node, ensure_ascii=False, indent=2)
    node_details_str = json.dumps(details, ensure_ascii=False, indent=2)
    
    # 采用直接字符串替换，彻底防范截断和正则解析错误
    final_html = HTML_TEMPLATE.replace("{tree_data_placeholder}", tree_data_str).replace("{node_details_placeholder}", node_details_str)
    
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(final_html)
        
    print(f"终极版 HTML 顺利生成写入：\n{OUTPUT_HTML}")

if __name__ == "__main__":
    main()
