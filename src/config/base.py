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
    auth_key = '299095cc-1330-11e5-b06a-a45e60bec08b'  # HMAC 签名密钥
    auth_timeout = 3  # 秒 请求有效期
    auth_key_name = 'X-Auth-Key'

    stream_hidden = {'tags': ['hidden']}

    # 其他配置
    max_history_length = 100
