"""require_model 的独立可运行测试

运行：.venv/Scripts/python.exe tests/require_model.py
与 tests/users_list.py 同一风格：可直接运行，非 pytest。
"""
import sys
from pathlib import Path

from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.exceptions import BadRequestError
from src.domains.users.schemas import CreateUserSchema
from src.utils.validate import require_model


class UserSchema(BaseModel):
    user_id: int
    username: str


def test_valid():
    payload = require_model({'user_id': 1, 'username': 'alice'}, UserSchema)
    assert isinstance(payload, UserSchema)
    assert payload.user_id == 1
    assert payload.username == 'alice'


def test_bad_type():
    try:
        require_model({'user_id': 'x', 'username': 'alice'}, UserSchema)
    except BadRequestError as e:
        assert e.msg == 'bad request'
    else:
        raise AssertionError('should raise BadRequestError')


def test_missing_field():
    try:
        require_model({'user_id': 1}, UserSchema)
    except BadRequestError as e:
        assert e.msg == 'bad request'
    else:
        raise AssertionError('should raise BadRequestError')


def test_create_user_semantics():
    # 与旧 require_str / optional_str 行为等价：
    # 必填 username 为空串或全空白 -> 拒绝
    for bad in ('', '   '):
        try:
            require_model({'username': bad}, CreateUserSchema)
        except BadRequestError:
            pass
        else:
            raise AssertionError(f'username={bad!r} should raise BadRequestError')
    # 可选字段缺省或 None -> 通过，值为 None
    payload = require_model({'username': 'alice'}, CreateUserSchema)
    assert payload.display_name is None
    assert payload.email is None
    # 全量合法 -> 通过
    payload = require_model(
        {'username': 'alice', 'display_name': 'A', 'email': 'a@b.com'}, CreateUserSchema
    )
    assert payload.username == 'alice'
    # strip_whitespace：首尾空白被去掉（与旧 require_str 原样存储不同）
    payload = require_model({'username': '  alice  '}, CreateUserSchema)
    assert payload.username == 'alice'


def main():
    test_valid()
    test_bad_type()
    test_missing_field()
    test_create_user_semantics()
    print('require_model: all tests passed')


if __name__ == '__main__':
    main()
