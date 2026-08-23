import httpx2

BASE_URL = 'http://127.0.0.1:8000'


def list_users(limit: int = 10):
    url = f'{BASE_URL}/users.list'

    data = {
        'limit': limit
    }

    with httpx2.Client(timeout=5.0) as client:
        resp = client.post(url, json=data)
        resp.raise_for_status()  # HTTP 层错误（4xx/5xx）直接抛出
        data = resp.json()

    # 业务层失败（code != 0）同样视为调用失败
    if data.get('code') != 0:
        raise RuntimeError(f'业务调用失败: code={data.get("code")}, msg={data.get("msg")}')

    return data


def main():
    data = list_users(5)
    users = data['data'] or []
    return users


if __name__ == '__main__':
    ret = main()
    print(ret)
