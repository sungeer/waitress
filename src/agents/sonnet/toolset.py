import time
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langgraph.config import get_config

from src.core import db


class QueryOrderInput(BaseModel):
    description: str = Field(description='订单描述，如"昨天的订单"、"最近一笔订单"')


class CancelOrderInput(BaseModel):
    order_id: str = Field(description='要取消的订单编号')


class CreateApprovalInput(BaseModel):
    order_id: str = Field(description='需要审批的订单编号')
    amount: float = Field(description='订单金额，从 query_order 结果中获取')


# 模拟订单数据
_mock_orders = {
    'ORD-2847': {
        'order_id': 'ORD-2847',
        'amount': 4800.00,
        'status': '已发货',
        'item': '工业传感器 X200',
        'created_at': '2026-05-15',
        'buyer': 'zhangsan',
    },
    'ORD-1803': {
        'order_id': 'ORD-1803',
        'amount': 350.00,
        'status': '待发货',
        'item': '办公文具套装',
        'created_at': '2026-05-15',
        'buyer': 'zhangsan',
    },
}


@tool(args_schema=QueryOrderInput)
def query_order(description: str) -> str:
    """根据描述查询用户最近的订单，返回订单详情（含金额、状态等）"""
    logger.info('in tools [query_order]')

    if '昨天' in description or '最近' in description:
        order = _mock_orders['ORD-2847']
    else:
        order = _mock_orders['ORD-1803']

    return (
        f'找到订单：{order["order_id"]}，'
        f'商品：{order["item"]}，'
        f'金额：¥{order["amount"]:.2f}，'
        f'状态：{order["status"]}，'
        f'日期：{order["created_at"]}，'
        f'买家：{order["buyer"]}'
    )


@tool(args_schema=CancelOrderInput)
def cancel_order(order_id: str) -> str:
    """取消指定订单并触发退款"""
    logger.info('in tools [cancel_order]')
    order = _mock_orders.get(order_id)
    if not order:
        return f'订单 [{order_id}] 不存在，无法取消'

    return f'订单 [{order_id}] 已取消，退款 ¥{order["amount"]:.2f} 将在 3 个工作日内退回原支付账户。'


@tool(args_schema=CreateApprovalInput)
def create_approval(order_id: str, amount: float) -> str:
    """创建审批记录到数据库并短信通知审批人。金额 > ¥1000 的订单取消需调用此工具"""
    logger.info('in tools [create_approval]')

    config = get_config()
    thread_id = config['configurable']['thread_id']

    now = int(time.time())
    approval_id = f'APR-{datetime.now().strftime("%Y%m%d")}-{now % 100000:05d}'

    sql_str = '''
        INSERT INTO approval_tasks (
            thread_id, order_id, status, created_at, updated_at
        ) VALUES (?, ?, 0, ?, ?)
    '''
    params = (thread_id, order_id, now, now)

    with db.begin() as cursor:
        cursor.execute(sql_str, params)

    logger.info(f'短信通知已发送：审批人，订单 [{order_id}] 取消审批待处理（编号：{approval_id}）')

    return (
        f'审批已提交（编号：{approval_id}）。'
        f'订单 [{order_id}] 金额 ¥{amount:.2f}。'
        f'已短信通知审批人，预计 24 小时内处理。审批通过后将自动取消并退款。'
    )
