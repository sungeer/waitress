import os
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent.parent


class BaseConfig:
    log_path = base_dir / 'logs/app_{time:YYYY-MM-DD}.log'

    jwt_algorithm = 'HS256'  # 加密算法
    jwt_access_token_expire_minutes = 30  # 访问令牌有效期 30分钟

    # SSO 配置
    sso_base_url = 'https://sso.company.com'
    sso_app_id = 'waitress'  # 本应用在 SSO 注册的 app_id
    sso_login_path = '/auth'  # SSO 登录页路径，拼接后: GET {sso_base_url}/auth?app_id=xxx&redirect_uri=xxx
    sso_verify_path = '/api/verify'  # 用户名密码校验接口
    sso_token_verify_path = '/api/token-verify'  # SSO token 换用户信息接口
    sso_timeout = 10  # 秒

    # 服务间认证（与 前端的后端 共享） 'openssl rand -hex 32'
    service_token = '786b96ed57229010676754c1c13c163a0fe777f3b8e8ff3569575fa5d766fb22'  # HMAC 签名密钥
    service_token_timeout = 30  # 秒 请求有效期

    stream_hidden = {'tags': ['hidden']}

    # 其他配置
    max_history_length = 100


class DevConfig(BaseConfig):
    is_debug = 1

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    # 'openssl rand -hex 32'
    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    db_path = base_dir / 'data/data.db'
    checkpoint_path = base_dir / 'data/checkpoints.db'

    # LLM 配置
    llm_common_url = os.getenv('ANTHROPIC_BASE_URL')
    llm_common_key = os.getenv('ANTHROPIC_AUTH_TOKEN')
    llm_common_model = os.getenv('ANTHROPIC_MODEL')

    llm_rag_key = 'sk_zaq1xsw2cde'
    llm_rag_url = 'http://127.0.0.1:6699/v1'

    rag_host = '127.0.0.1'
    rag_port = 9903
    rag_model = 'bge-m3'


class ProdConfig(BaseConfig):
    is_debug = 0

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    db_path = base_dir / 'data/data.db'
    checkpoint_path = base_dir / 'data/checkpoints.db'

    # LLM 配置
    llm_common_url = os.getenv('ANTHROPIC_BASE_URL')
    llm_common_key = os.getenv('ANTHROPIC_AUTH_TOKEN')
    llm_common_model = os.getenv('ANTHROPIC_MODEL')

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
