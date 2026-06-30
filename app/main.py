
import logging
from contextlib import asynccontextmanager
from app.infrastructure.storage.redis import get_redis


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.storage.postgres import get_postgres

from app.infrastructure.logging import setup_logging
from app.interface.endpoints.routes import router
from core.config import get_settings
from app.interface.errors.exception_handlers import register_exception_handlers



# 1. 加载配置信息
settings = get_settings()

# 2. 初始化日志系统
setup_logging()
logger = logging.getLogger(__name__)
logger.info("测试")


# 3. 定义FastAPI路由tags标签
openapi_tags=[
    {
        "name" : "状态模块",
        "description": "包含**状态检测** 等API接口，用于检测系统的运行状态。"
    }
]


@asynccontextmanager
async def lifespan(app:FastAPI):
    """创建FastAPI应用程序生命周期上下文管理"""
    # 1.打印日志标识程序开始了
    logger.info("MoocManus正在初始化")

    # 2.初始化Redis缓存客户端
    redis = get_redis()
    await redis.init()

    # 3. 初始化Postgres客户端
    postgres = get_postgres()
    await postgres.init()

    try:
        # lifespan 节点/分界
        yield
    finally:
        await redis.shutdown()
        await postgres.shutdown()
        logger.info("MoocManus正在关闭。。。")

# 4.创建moocmanus应用实例
app = FastAPI(
    title= "MoocManus通用智能体",
    description= "MoocManus是一个通用AI Agent系统，可以完全私有部署，可以使用A2A+MCP连接Agent/Tool，同时支持在沙箱中运行各种内置工具和操作",
    lifespan= lifespan,
    openapi_tags=openapi_tags,
    version = "1.0.0"
)

# 5. 配置CORS中间件,解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 6.注册错误处理器
register_exception_handlers(app)




# 7.集成路由
app.include_router(router,prefix="/api")




