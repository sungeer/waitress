import json
import unittest
from unittest.mock import patch

from src.domains.chat import service, tools
from src.domains.chat.errors import UpstreamError
from src.utils import validate
from src.utils.exceptions import ParamError, UpstreamUnavailableError


def tool_call(call_id='call_1', arguments='{"latitude": 39.9, "longitude": 116.4}'):
    return {
        'id': call_id,
        'type': 'function',
        'function': {
            'name': 'get_weather',
            'arguments': arguments,
        },
    }


def tool_turn(*calls):
    return {
        'finish_reason': 'tool_calls',
        'message': {
            'role': 'assistant',
            'content': None,
            'reasoning_content': '需要查询天气',
            'tool_calls': list(calls),
        },
    }


def text_turn(content):
    return {
        'finish_reason': 'stop',
        'message': {
            'role': 'assistant',
            'content': content,
        },
    }


class ReactServiceTest(unittest.IsolatedAsyncioTestCase):

    async def test_returns_text_when_model_answers_directly(self):
        seen = []

        async def fake_chat(messages, tools=None, tool_choice=None):
            seen.append((messages, tools, tool_choice))
            return text_turn('今天晴。')

        with patch.object(service.upstream, 'chat', new=fake_chat):
            answer = await service.react('天气怎么样？', 39.9, 116.4)

        self.assertEqual(answer, '今天晴。')
        self.assertEqual(seen[0][1], service.tools.weather_tools)

    async def test_executes_tool_and_returns_text(self):
        seen = []
        executed = []

        async def fake_chat(messages, tools=None, tool_choice=None):
            seen.append((messages, tools, tool_choice))
            if len(seen) == 1:
                return tool_turn(tool_call())
            return text_turn('当前 20 度。')

        async def fake_execute(call):
            executed.append(call)
            return {'temperature': 20}

        with patch.object(service.upstream, 'chat', new=fake_chat), \
                patch.object(service.tools, 'execute', new=fake_execute):
            answer = await service.react('天气？', 39.9, 116.4)

        self.assertEqual(answer, '当前 20 度。')
        self.assertEqual(len(executed), 1)
        self.assertEqual(seen[1][0][-1]['role'], 'tool')
        self.assertEqual(seen[1][0][-1]['tool_call_id'], 'call_1')
        self.assertEqual(
            json.loads(seen[1][0][-1]['content']),
            {'temperature': 20},
        )

    async def test_stops_after_three_tool_calls_and_forces_text(self):
        seen = []
        executed = []

        async def fake_chat(messages, tools=None, tool_choice=None):
            seen.append((messages, tools, tool_choice))
            if tool_choice == 'none':
                return text_turn('查询次数已用完。')
            return tool_turn(tool_call(f'call_{len(executed) + 1}'))

        async def fake_execute(call):
            executed.append(call)
            return {'temperature': 20}

        with patch.object(service.upstream, 'chat', new=fake_chat), \
                patch.object(service.tools, 'execute', new=fake_execute):
            answer = await service.react('天气？', 39.9, 116.4)

        self.assertEqual(answer, '查询次数已用完。')
        self.assertEqual(len(executed), 3)
        self.assertEqual(seen[-1][1], service.tools.weather_tools)
        self.assertEqual(seen[-1][2], 'none')

    async def test_tool_error_is_returned_as_observation(self):
        seen = []

        async def fake_chat(messages, tools=None, tool_choice=None):
            seen.append(messages)
            if len(seen) == 1:
                return tool_turn(tool_call())
            return text_turn('暂时查不到。')

        async def fake_execute(call):
            return {'error': 'weather upstream unavailable'}

        with patch.object(service.upstream, 'chat', new=fake_chat), \
                patch.object(service.tools, 'execute', new=fake_execute):
            answer = await service.react('天气？', 39.9, 116.4)

        self.assertEqual(answer, '暂时查不到。')
        self.assertIn('weather upstream unavailable', seen[1][-1]['content'])

    async def test_upstream_error_maps_to_unavailable(self):
        async def fake_chat(messages, tools=None, tool_choice=None):
            raise UpstreamError('boom')

        with patch.object(service.upstream, 'chat', new=fake_chat):
            with self.assertRaises(UpstreamUnavailableError):
                await service.react('天气？', 39.9, 116.4)


class ValidateNumberTest(unittest.TestCase):

    def test_rejects_nan(self):
        with self.assertRaises(ParamError):
            validate.require_number(
                {'latitude': float('nan')}, 'latitude', -90, 90
            )

    def test_rejects_bool(self):
        with self.assertRaises(ParamError):
            validate.require_number({'latitude': True}, 'latitude')


class ToolsTest(unittest.IsolatedAsyncioTestCase):

    async def test_invalid_arguments_json(self):
        result = await tools.execute(tool_call(arguments='not json'))
        self.assertIn('error', result)

    async def test_out_of_range_coordinates(self):
        result = await tools.execute(
            tool_call(arguments='{"latitude": 100, "longitude": 0}')
        )
        self.assertIn('error', result)

    async def test_unknown_tool(self):
        call = {
            'id': 'call_1',
            'type': 'function',
            'function': {'name': 'unknown', 'arguments': '{}'},
        }
        result = await tools.execute(call)
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
