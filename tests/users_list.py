import httpx2 as httpx

BASE_URL = 'http://127.0.0.1:8848'


def list_users(limit: int = 10):
    url = f'{BASE_URL}/users.list'

    data = {
        'limit': limit
    }

    resp = httpx.post(url, json=data, timeout=5.0, verify=False)
    resp.raise_for_status()  # HTTP 层错误（4xx/5xx）直接抛出
    data = resp.json()

    # 业务层失败（success 为假）同样视为调用失败
    if not data.get('success'):
        raise RuntimeError(f'business call failed: error={data.get("error")}')

    return data


def main():
    data = list_users(5)
    users = data['data'] or []
    return users


if __name__ == '__main__':
    ret = main()
    print(ret)
