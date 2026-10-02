import socket

BASE_URL = ('127.0.0.1', 8848)


def abort_mid_body(path='/users.get'):
    """发一半请求体就断开 模拟客户端中途退出"""
    head = (
        f'POST {path} HTTP/1.1\r\n'
        'Host: 127.0.0.1:8848\r\n'
        'Content-Type: application/json\r\n'
        'Content-Length: 100\r\n'
        '\r\n'
    )
    half_body = '{"user_id":'  # 只发一半 剩下的不发 直接断开

    s = socket.create_connection(BASE_URL, timeout=5.0)
    s.sendall(head.encode() + half_body.encode())
    s.close()


def main():
    abort_mid_body()


if __name__ == '__main__':
    main()
    print('sent half body then closed')
