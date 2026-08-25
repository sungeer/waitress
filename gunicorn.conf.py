from dotenv import load_dotenv

_env_file = '/srv/env/waitress.env'
load_dotenv(_env_file)

bind = '0.0.0.0:8848'
chdir = '/srv/waitress'
pidfile = '/srv/run/waitress.pid'

workers = 1
worker_class = 'uvicorn.workers.UvicornWorker'

errorlog = '/srv/logs/gunicorn.log'
