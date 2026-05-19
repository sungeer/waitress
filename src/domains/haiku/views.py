from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from src.core.response import ok
from src.core.exceptions import BadRequestError, BusinessError
from src.core.codes import BizCode
from src.domains.haiku import service
from src.domains.haiku.schema import CancelInSchema, ApprovalInSchema


# 发起订单取消请求
async def cancel_order(request):
    data = await request.json()
    try:
        data = CancelInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = await run_in_threadpool(service.start_cancel, data.content, data.approver_id)
    if result.get('need_approval'):
        return ok({'thread_id': result['thread_id']}, result.get('message', ''))
    return ok(result.get('reply'))


# 获取待审批项
async def pending(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = await service.get_pending(data.thread_id)
    if result is None:
        raise BusinessError(BizCode.RESOURCE_NOT_FOUND, '无待审批项')
    return ok(result)


# 审批通过
async def approve(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    await run_in_threadpool(service.approve, data.thread_id, data.operator)
    return ok(None, '审批通过，订单已取消并触发退款')


# 审批拒绝
async def reject(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    await run_in_threadpool(service.reject, data.thread_id, data.operator, data.reason)
    return ok(None, '已拒绝，结果已通知用户')
