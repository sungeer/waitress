from dotenv import load_dotenv

_env_file = '/srv/env/waitress.env'
load_dotenv(_env_file)

bind = '0.0.0.0:8848'
chdir = '/srv/waitress'
pidfile = '/srv/run/waitress.pid'

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

keepalive = 5  # 保持客户端连接的时长
timeout = 30  # worker 处理单个请求超时时间(秒)
graceful_timeout = 30  # 平滑重启等待时长(秒)

accesslog = None  # 关闭访问日志
errorlog = '-'  # 改为 '-'，将 Gunicorn 自身错误输出到 stderr
loglevel = 'info'
capture_output = False  # 防止 Loguru 的日志被 Gunicorn 再抓取一次
