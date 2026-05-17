import httpx

BASE = 'http://127.0.0.1:8000'


def test_chat():
    data = {
        'messages': '#weather#上海天气情况。',
        'stream': False,
        'message_id': '1778977269578',
        'is_think': False
    }
    with httpx.Client() as client:
        resp = client.post(f'{BASE}/sonnet.chat', json=data)
        print(f'状态码: {resp.status_code}')
        print(f'响应体: {resp.text}')
        return resp.json()


if __name__ == '__main__':
    data = test_chat()
    print(f'解析结果: {data}')
