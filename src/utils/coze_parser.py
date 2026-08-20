# agent_parser.py
"""
Coze 输出解析器

将 Coze 平台输出的非结构化文本解析为结构化字典。
专为无法直接 JSON 格式化的场景设计。
"""

import re
from typing import Dict


def parse_output(text: str) -> Dict[str, str]:
    """
    解析 Agent 输出的分段文本。

    支持格式：
        ### 标题1
        内容1

        ### 标题2
        内容2

    Args:
        text: Agent 原始输出文本

    Returns:
        标题到内容的映射字典
    """
    if not text or not text.strip():
        return {}

    sections = re.split(r'\n(?=###)', text.strip())
    result = {}

    for section in sections:
        title_match = re.match(r'###\s*(.*?)\s*\n', section)
        if not title_match:
            continue

        title = title_match.group(1).strip()
        body = section[title_match.end():].strip()
        result[title] = body

    return result


if __name__ == '__main__':
    content = '### name\nTom\n\n### age\n29'
    data = parse_output(content)
    print(data)
