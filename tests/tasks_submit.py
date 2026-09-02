import httpx2 as httpx

BASE_URL = 'http://127.0.0.1:8000'


def submit_task(user_id: int):
    url = f'{BASE_URL}/tasks.submit'

    payload = {
        'user_id': user_id
    }

    resp = httpx.post(url, json=payload, timeout=5.0, verify=False)
    resp.raise_for_status()  # HTTP 层错误（4xx/5xx）直接抛出
    data = resp.json()

    # 业务层失败（code != 0）同样视为调用失败
    if data.get('code') != 0:
        raise RuntimeError(f'business call failed: code={data.get("code")}, msg={data.get("msg")}')

    return data


def main():
    data = submit_task(1)
    return data


if __name__ == '__main__':
    ret = main()
    print(ret)
