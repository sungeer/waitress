import time
import hmac
import hashlib

from src.core.config import settings
from src.core.exceptions import UnauthorizedError


# 生成签名 示例
def get_signature(key, data):
    hmac_obj = hmac.new(
        key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    )
    return hmac_obj.hexdigest()


# 请求示例
def send_data(server_info):
    import httpx

    key = 'asdfasdfasdfasdf'  # 双方约定的 secret_key

    timestamp = str(time.time())

    # 生成签名
    signature = get_signature(key, timestamp)

    headers = {
        'X-Auth-Signature': signature,
        'X-Auth-Timestamp': timestamp,
    }

    url = 'http://127.0.0.1:8000/api/asset/'

    with httpx.Client() as client:
        response = client.post(url=url, json=server_info, headers=headers)

    return response


def verify_service_signature(request):
    """验证服务间请求的 HMAC 签名

    从请求头提取 X-Auth-Signature 和 X-Auth-Timestamp，
    用共享密钥重算签名并比对，同时校验时间戳防止重放攻击。
    """
    signature = request.headers.get('X-Auth-Signature')
    timestamp = request.headers.get('X-Auth-Timestamp')

    if not signature or not timestamp:
        raise UnauthorizedError('服务间认证信息缺失')

    # 校验时间戳，防止重放攻击
    try:
        elapsed = time.time() - float(timestamp)
        if elapsed > settings.service_token_timeout:
            raise UnauthorizedError('请求已过期')
        if elapsed < 0:
            raise UnauthorizedError('时间戳异常')
    except ValueError:
        raise UnauthorizedError('时间戳格式错误')

    # 用同样算法重算签名
    expected = hmac.new(
        settings.service_token.encode('utf-8'),
        timestamp.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()

    # 常量时间比对，防时序攻击
    if not hmac.compare_digest(signature, expected):
        raise UnauthorizedError('签名验证失败')
