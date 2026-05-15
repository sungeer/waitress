from pydantic import ValidationError
from starlette.concurrency import run_in_threadpool

from src.core.response import ok
from src.core.exceptions import BadRequestError, BusinessError
from src.core.codes import BizCode
from src.domains.haiku import service
from src.domains.haiku.schema import ThreadInSchema, ApprovalInSchema


# 发起通知请求
async def notify(request):
    data = await request.json()
    try:
        data = ThreadInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    thread_id = await run_in_threadpool(service.start_notify, data.content, data.approver_id)
    return ok({'thread_id': thread_id}, '通知请求已提交，请等待审批')


# 获取待审批的通知内容
async def pending(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    result = service.get_pending(data.thread_id)
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
    return ok(None, '审批通过，通知已发送')


# 审批拒绝
async def reject(request):
    data = await request.json()
    try:
        data = ApprovalInSchema.model_validate(data)
    except ValidationError:
        raise BadRequestError()

    await run_in_threadpool(service.reject, data.thread_id, data.operator)
    return ok(None, '已拒绝，通知未发送')
