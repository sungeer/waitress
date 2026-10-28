import httpx2 as httpx

BASE_URL = 'http://127.0.0.1:8848'


def chat_ask():
    url = f'{BASE_URL}/chat.structured'

    resp = httpx.post(url, timeout=15.0, verify=False)
    resp.raise_for_status()  # HTTP 层错误（4xx/5xx）直接抛出
    data = resp.json()

    # 业务层失败（code != 0）同样视为调用失败
    if data.get('code') != 0:
        raise RuntimeError(f'business call failed: code={data.get("code")}, msg={data.get("msg")}')

    return data


def main():
    data = chat_ask()
    return data


if __name__ == '__main__':
    ret = main()
    print(ret)
