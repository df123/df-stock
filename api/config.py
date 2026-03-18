"""
API配置文件
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """API配置"""
    
    # API配置
    API_TITLE: str = "ETF量化分析系统 API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "ETF数据获取与技术分析API"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:8080", "http://localhost:3000", "http://127.0.0.1:8080"]
    
    # 数据库配置
    DB_PATH: str = "db/etf_data.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    """获取配置单例"""
    return Settings()
