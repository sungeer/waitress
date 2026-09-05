import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import URL

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 加载 .env 若存在
_dotenv_path = BASE_DIR / '.env'
if _dotenv_path.exists():
    load_dotenv(_dotenv_path)


def _require(name: str) -> str:
    # 必填环境变量，缺失时启动即报错（fail fast）
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f'Missing required environment variables: {name}')
    return value


# 环境
_ENVIRONMENTS = ('development', 'testing', 'production')
ENVIRONMENT = _require('ENVIRONMENT')
if ENVIRONMENT not in _ENVIRONMENTS:
    raise ValueError(f'Invalid ENVIRONMENT: {ENVIRONMENT}，only allowed {sorted(_ENVIRONMENTS)}')

# 日志
# LOG_FILE = BASE_DIR / 'logs/waitress.log'
LOG_FILE = Path(os.getenv('LOG_FILE', default=str(BASE_DIR / 'logs/waitress.log')))

# 应用版本
VERSION = '26.0906.0712'

# JWT
JWT_ALGORITHM = 'HS256'  # 加密算法
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', default='600'))  # 访问令牌有效期 600分钟
AUTH_KEY = _require('AUTH_KEY')  # HMAC 签名密钥 'openssl rand -hex 32'
JWT_SECRET_KEY = _require('JWT_SECRET_KEY')  # JWT 签名密钥

# CORS 允许的来源 逗号分隔
ORIGINS = _require('ORIGINS').split(',')

# MySQL
DB_HOST = _require('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', default='3306'))
DB_USER = _require('DB_USER')
DB_PASSWORD = _require('DB_PASSWORD')  # 数据库密码
DB_NAME = _require('DB_NAME')
# 密码只来自 DB_PASSWORD 单点，便于后续对密码加密后在此解密
DB_URL = URL.create(
    drivername='mysql+pymysql',
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)
