resp = {
    'id': 'f37b38bf-5dae-4eba-be6a-f769188e7296',
    'object': 'chat.completion',
    'created': 1793407875,
    'model': 'deepseek-flash',
    'choices': [
        {
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': '',
                'tool_calls': [
                    {
                        'index': 0,
                        'id': 'call_00_8Vy1X4zLSRiriEZQdkoq3419',
                        'type': 'function',
                        'function': {
                            'name': 'get_weather',
                            'arguments': '{"latitude": 39.9042, "longitude": 116.4074}'
                        }
                    }
                ]
            },
            'logprobs': None,
            'finish_reason': 'tool_calls'
        }
    ],
    'usage': {
        'prompt_tokens': 451,
        'completion_tokens': 61,
        'total_tokens': 512,
        'prompt_tokens_details': {'cached_tokens': 256},
        'prompt_cache_hit_tokens': 256,
        'prompt_cache_miss_tokens': 195
    },
    'system_fingerprint': 'bc19ba97cbe016479903222bb1578db6'
}

end = {
    'id': 'e943d7b1-8f0a-4d2d-b0af-3974eb0c979c',
    'object': 'chat.completion',
    'created': 1793407882,
    'model': 'deepseek-flash',
    'choices': [
        {
            'index': 0,
            'message': {
                'role': 'assistant',
                'content': '坐标 (39.9042, 116.4074) 当前天气：\n\n- 时间：2026-10-31 00:45\n- 气温：6.6°C\n- 风速：3.1（风向 87°）\n- 天气：晴（weathercode 0，白天）\n\n夜间气温较低，外出注意保暖。'
            },
            'logprobs': None,
            'finish_reason': 'stop'
        }
    ],
    'usage': {
        'prompt_tokens': 583,
        'completion_tokens': 76,
        'total_tokens': 659,
        'prompt_tokens_details': {'cached_tokens': 384},
        'prompt_cache_hit_tokens': 384,
        'prompt_cache_miss_tokens': 199
    },
    'system_fingerprint': 'bc19ba97cbe016479903222bb1578db6'
}
