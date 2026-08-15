import httpx

BASE = 'http://127.0.0.1:8000'


def foo_a():
    data = {
        'task_id': '1779198781166',
    }

    with httpx.Client() as client:
        resp = client.post(f'{BASE}/tasks.submit.async', json=data, timeout=5)
        return resp.json()


def foo_b():
    data = {
        'task_id': '1779198781188',
    }

    with httpx.Client() as client:
        resp = client.post(f'{BASE}/tasks.submit.sync', json=data, timeout=5)
        return resp.json()


def foo_c():
    data = {
        'task_id': '1779198781199',
    }

    with httpx.Client() as client:
        resp = client.post(f'{BASE}/tasks.submit.async_blocking', json=data, timeout=5)
        return resp.json()


if __name__ == '__main__':
    ret = foo_a()
    print(f'解析结果: {ret}')
    print('==============================')
    ret = foo_b()
    print(f'解析结果: {ret}')
    print('==============================')
    ret = foo_c()
    print(f'解析结果: {ret}')
