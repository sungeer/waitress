import os

from src.config.base import BaseConfig, base_dir


class ProductionConfig(BaseConfig):
    environment = 'production'

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    checkpoint_path = base_dir / 'data/chp.db'

    # MySQL 配置
    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_passwd = 'admin'
    db_name = 'viper'

    # LLM 配置
    llm_url = os.getenv('LLM_BASE_URL')
    llm_key = os.getenv('LLM_AUTH_TOKEN')
    llm_model = os.getenv('LLM_MODEL')
