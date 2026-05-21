import time
import hmac
import hashlib


# 生成签名
def get_signature(key, data):
    hmac_obj = hmac.new(
        key.encode('utf-8'),
        data.encode('utf-8'),
        hashlib.sha256
    )
    return hmac_obj.hexdigest()


def send_data(user_info):
    import httpx

    key = 'asdfasdfasdfasdf'  # 双方约定的 secret_key

    timestamp = str(time.time())

    # 生成签名
    signature = get_signature(key, timestamp)

    headers = {
        'X-Auth-Signature': signature,
        'X-Auth-Timestamp': timestamp,
    }

    url = 'http://127.0.0.1:8000/auth.token'

    with httpx.Client() as client:
        response = client.post(url=url, json=user_info, headers=headers)

    return response


if __name__ == '__main__':
    data = {
        'user_id': 123,
        'username': 'facai'
    }
    jwt_token = send_data(data)
    print(jwt_token)
