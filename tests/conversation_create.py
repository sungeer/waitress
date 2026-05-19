import httpx

BASE = 'http://127.0.0.1:8000'


def test_create_conversation(title='测试会话'):
    with httpx.Client() as client:
        resp = client.post(f'{BASE}/sonnet.conversation.create', json={'title': title})
        print(f'状态码: {resp.status_code}')
        print(f'响应体: {resp.text}')
        return resp.json()


if __name__ == '__main__':
    data = test_create_conversation()
    print(f'解析结果: {data}')  # '1779171239219'
