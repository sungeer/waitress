import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent


class BaseConfig:
    log_path = base_dir / 'logs/app_{time:YYYY-MM-DD}.log'

    jwt_algorithm = 'HS256'  # 加密算法
    jwt_access_token_expire_minutes = 30  # 访问令牌有效期 30分钟

    # SSO 配置
    sso_base_url = 'https://sso.company.com'
    sso_verify_path = '/api/verify'
    sso_timeout = 10  # 秒

    # 其他配置
    max_history_length = 100

    checkpoint_db = base_dir / 'data/checkpoints.db'

    hidden_config = {'tags': ['hidden']}


class DevConfig(BaseConfig):
    is_debug = 1

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    # 'openssl rand -hex 32'
    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'jack'
    db_passwd = 'zaq1xsw2'
    db_name = 'waitress'

    # LLM 配置
    llm_common_url = 'http://127.0.0.1:7788/v1'
    llm_common_key = 'sk_zaq1xsw2cde'
    llm_common_model = 'qwen3-235b-a22b'

    llm_think_url = 'http://127.0.0.1:6699/v1'
    llm_think_key = 'sk_zaq1xsw2cde'
    llm_think_model = 'qwen3-300b-a22b'

    llm_rag_key = 'sk_zaq1xsw2cde'
    llm_rag_url = 'http://127.0.0.1:6699/v1'

    rag_host = '127.0.0.1'
    rag_port = 9903
    rag_model = 'bge-m3'


class ProdConfig(BaseConfig):
    is_debug = 0

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'jack'
    db_passwd = 'zaq1xsw2'
    db_name = 'waitress'

    # LLM 配置
    llm_common_url = 'http://127.0.0.1:7788/v1'
    llm_common_key = 'sk_zaq1xsw2cde'
    llm_common_model = 'qwen3-235b-a22b'

    llm_think_url = 'http://127.0.0.1:6699/v1'
    llm_think_key = 'sk_zaq1xsw2cde'
    llm_think_model = 'qwen3-300b-a22b'

    llm_rag_key = 'sk_zaq1xsw2cde'
    llm_rag_url = 'http://127.0.0.1:6699/v1'

    rag_host = '127.0.0.1'
    rag_port = 9903
    rag_model = 'bge-m3'


config_map = {
    'dev': DevConfig,
    'prod': ProdConfig
}

is_debug = os.getenv('DEBUG') == '1'

config_name = 'dev' if is_debug else 'prod'

settings = config_map.get(config_name, ProdConfig)
