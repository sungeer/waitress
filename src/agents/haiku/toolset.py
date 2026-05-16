from pydantic import BaseModel, Field
from langchain_core.tools import tool


class QueryOrderInput(BaseModel):
    description: str = Field(description='订单描述，如"昨天的订单"、"最近一笔订单"')


class CancelOrderInput(BaseModel):
    order_id: str = Field(description='要取消的订单编号')
    reason: str = Field(description='取消原因')


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
    # 模拟：根据关键词匹配
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
def cancel_order(order_id: str, reason: str) -> str:
    """取消指定订单，并自动触发退款流程"""
    order = _mock_orders.get(order_id)
    if not order:
        return f'订单 [{order_id}] 不存在，无法取消'

    return (
        f'订单 [{order_id}] 已取消，退款 ¥{order["amount"]:.2f} 将在 3 个工作日内退回原支付账户。'
        f'取消原因：{reason}'
    )
