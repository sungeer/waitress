import httpx

BASE = 'http://127.0.0.1:8000'


def test_chat():
    data = {
        'messages': '#weather#上海天气情况如何？',
        'stream': True,
        'message_id': '1779184493986',
        'is_think': False
    }
    with httpx.Client() as client:
        with client.stream('POST', f'{BASE}/opus.chat', json=data) as resp:
            print(f'状态码: {resp.status_code}')
            print('--- 流式输出 ---')
            for line in resp.iter_lines():
                if not line.strip():
                    continue
                print(line, flush=True)


if __name__ == '__main__':
    test_chat()
