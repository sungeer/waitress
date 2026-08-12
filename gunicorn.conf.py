from dotenv import load_dotenv

_env_file = '/srv/env/waitress.env'
load_dotenv(_env_file)

bind = '0.0.0.0:8848'
chdir = '/srv/waitress'
pidfile = '/srv/run/waitress.pid'

workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'

keepalive = 5  # 保持客户端连接的时长
timeout = 120  # worker 处理单个请求超时时间(秒)
graceful_timeout = 30  # 平滑重启等待时长(秒)
# max_requests = 1000  # 防止内存泄漏，worker处理1000个请求后重启
# max_requests_jitter = 50  # 添加随机抖动，防止worker同时重启

capture_output = True
# accesslog = '/srv/logs/access.log'
accesslog = None  # 不记录访问日志，业务日志已覆盖
errorlog = '/srv/logs/waitress.log'
loglevel = 'info'
