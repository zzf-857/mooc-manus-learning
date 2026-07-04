from pydantic import BaseModel, ConfigDict, HttpUrl, Field


class LLMConfig(BaseModel):
    """语言模型配置"""
    base_url: HttpUrl = "https://api.deepseek.com"  # 基础URL地址
    api_key: str = ""  # API密钥
    model_name: str = "deepseek-reasoner"  # 推理模型如果传递了tools底层会自动切换到deepseek-chat
    temperature: float = Field(default=0.7)  # 温度
    max_tokens: int = Field(8192, ge=0) # 最大输出token数



class AppConfig(BaseModel):
    """要用配置信息，包含Agent配置、LLM提供商、A2A网络、MCP服务配置等"""
    llm_config: LLMConfig #语言模型配置

    # Pydantic配置，允许传递额外的字段初始化
    model_config = ConfigDict(extra="allow")

    