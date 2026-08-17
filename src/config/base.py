from pathlib import Path

from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent.parent

# development
dotenv_path = base_dir / '.env'
if dotenv_path.exists():
    load_dotenv(dotenv_path)


class BaseConfig:
    version = '26.0817.0956'

    log_path = base_dir / 'logs/app.log'  # 常规日志（INFO及以上）
    error_log_path = base_dir / 'logs/error.log'  # 错误日志（仅ERROR+）

    jwt_algorithm = 'HS256'  # 加密算法
    jwt_access_token_expire_minutes = 30  # 访问令牌有效期 30分钟

    # 'openssl rand -hex 32'
    auth_key = '299095cc-1330-11e5-b06a-a45e60bec08b'  # HMAC 签名密钥
    auth_timeout = 3  # 秒 请求有效期
    auth_key_name = 'X-Auth-Key'
