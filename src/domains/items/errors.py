from src.core.codes import BizCode
from src.core.exceptions import BusinessError


# 在 service 层直接抛出 raise ItemNotFoundError() 即可
class ItemNotFoundError(BusinessError):

    def __init__(self):
        super().__init__(BizCode.ITEM_NOT_FOUND, BizCode.ITEM_NOT_FOUND.message)


class StockInsufficientError(BusinessError):

    def __init__(self):
        super().__init__(BizCode.STOCK_INSUFFICIENT, BizCode.STOCK_INSUFFICIENT.message)
