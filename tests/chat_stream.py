import json
import time

import httpx2 as httpx

URL = 'http://127.0.0.1:8848/agent.stream'


def main():
    started = time.perf_counter()
    count = 0
    parts = []

    with httpx.Client() as client:
        with client.stream('POST', URL) as response:
            print(f'POST {URL} -> {response.status_code} {response.headers.get("content-type")}')

            for line in response.iter_lines():
                if not line:
                    continue

                delta = json.loads(line)['delta']
                parts.append(delta)
                count += 1
                print(f'[{count:>3}] +{time.perf_counter() - started:5.2f}s  {delta}')

    text = ''.join(parts)
    print(f'\n{count} 块 / {len(text)} 字 / {time.perf_counter() - started:.2f}s')
    print(f'全文：{text}')


if __name__ == '__main__':
    main()
