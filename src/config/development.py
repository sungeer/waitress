import os

from src.config.base import BaseConfig, base_dir


class DevelopmentConfig(BaseConfig):
    environment = 'development'

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    # 'openssl rand -hex 32'
    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    checkpoint_path = base_dir / 'data/chp.db'

    # MySQL 配置
    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_passwd = 'admin'
    db_name = 'viper'

    # LLM 配置
    llm_common_url = os.getenv('ANTHROPIC_BASE_URL')
    llm_common_key = os.getenv('ANTHROPIC_AUTH_TOKEN')
    llm_common_model = os.getenv('ANTHROPIC_MODEL')

    llm_rag_key = 'sk_zaq1xsw2cde'
    llm_rag_url = 'http://127.0.0.1:6699/v1'

    rag_host = '127.0.0.1'
    rag_port = 9903
    rag_model = 'bge-m3'
