import httpx

BASE = 'http://127.0.0.1:8000'


def test_chat():
    data = {
        'messages': '帮我取消昨天的订单。',
        'stream': False,
        'message_id': '1779198781135',
        'is_think': False
    }
    with httpx.Client() as client:
        resp = client.post(f'{BASE}/haiku.chat', json=data, timeout=60)
        print(f'状态码: {resp.status_code}')
        print(f'响应体: {resp.text}')
        return resp.json()


if __name__ == '__main__':
    data = test_chat()
    print(f'解析结果: {data}')
