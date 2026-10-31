import httpx2 as httpx

BASE_URL = 'http://127.0.0.1:8848'


def chat_react(question: str):
    url = f'{BASE_URL}/chat.react'

    payload = {
        'question': question
    }

    resp = httpx.post(url, json=payload, timeout=60.0, verify=False)
    resp.raise_for_status()  # HTTP 层错误（4xx/5xx）直接抛出
    data = resp.json()

    # 业务层失败（success 为假）同样视为调用失败
    if not data.get('success'):
        raise RuntimeError(f'business call failed: error={data.get("error")}')

    return data


def main():
    data = chat_react('帮我查询经纬度116.39,39.90的天气')
    return data


if __name__ == '__main__':
    ret = main()
    print(ret)
