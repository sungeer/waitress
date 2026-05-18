from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field
from langchain_core.tools import tool


class WeatherInput(BaseModel):
    city: str = Field(description='城市名称')


@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    logger.info('in tools [get_weather]')
    weather_data = {
        '北京': '晴，25°C，微风',
        '上海': '多云，28°C，东南风3级',
        '深圳': '阵雨，30°C，西南风2级',
    }
    return weather_data.get(city, f'未找到[{city}]的天气数据')


@tool
def get_current_time() -> str:
    """获取当前系统时间"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
