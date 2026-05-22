import os

from src.config.development import DevelopmentConfig
from src.config.production import ProductionConfig
from src.config.testing import TestingConfig

config_map = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

config_name = os.getenv('CONFIG_NAME', default='production')

settings = config_map.get(config_name)
