import os

from src.config.base import BaseConfig, base_dir


class DevelopmentConfig(BaseConfig):
    environment = 'development'

    origins = ['http://127.0.0.1:8080']  # cors 允许的来源 前端应用使用的端口

    # 'openssl rand -hex 32'
    jwt_secret_key = 'cb6103ca0209a5ae546ebea25acfafd5bcebe9ffbd37cb9ad58704c53fee99c1'

    # MySQL 配置
    db_host = '127.0.0.1'
    db_port = 3306
    db_user = 'root'
    db_passwd = 'admin'
    db_name = 'viper'
