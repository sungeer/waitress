import time

import openai
from pymilvus import connections, Collection


client = openai.OpenAI(
    api_key="your-api-key",
    base_url="your-base-url"
)  # wx AsyncOpenAI


connections.connect(host='localhost', port='19530')

# 获取 预先建好的宪法集合
collection = Collection("constitution_collection")
# 加载集合到内存中
collection.load()

user_question = "我国的宪法第一条是什么"
print(f"用户问题: {user_question}\n")

# 向量化 用户的问题
max_retries = 3
for attempt in range(1, max_retries + 1):
    try:
        embeddings = client.embeddings.create(
            model="text-embedding-3-small",
            input=user_question
        )
        break
    except Exception as e:
        print(f"向量化失败(第{attempt}次): {e}")
        if attempt < max_retries:
            time.sleep(2)
        else:
            exit(1)

question_embedding = [data.embedding for data in embeddings.data]

# 在 Milvus 中进行向量相似度搜索
search_params = {
    "metric_type": "COSINE",  # 向量 相似度计算方式
    "params": {"nprobe": 10}  # 搜索范围控制参数
}

try:
    search_results = collection.search(
        data=question_embedding,  # 问题的向量 list
        anns_field="vector",  # 在哪个字段里搜
        param=search_params,
        limit=3,  # 只取最相关的 3 条结果
        consistency_level='Strong',
        partition_names=['userknowledge'],
        output_fields=['text','field']  # 搜索结果要返回原始文本内容
    )  # wx to_thread_pool
except Exception as e:
    print(f"向量检索失败: {e}")
    exit(1)

# 提取搜索到的文本内容
retrieved_texts = []
for hits in search_results:
    for hit in hits:
        retrieved_texts.append(hit.entity.get("text"))

print(f"检索到的相关宪法条文:\n{'-' * 30}")
for i, text in enumerate(retrieved_texts):
    print(f"{i + 1}. {text}\n")

# 把找到的背景知识和用户问题拼起来
context_str = "\n".join([f"{i + 1}. {t}" for i, t in enumerate(retrieved_texts)])

prompt = f"""\
你是一个严谨的法律助手。请仅仅根据以下提供的【参考资料】来回答用户的【问题】。
如果参考资料中没有包含答案，请回答“根据提供的资料无法回答”。
不要自己编造信息。

【参考资料】：
{context_str}

【问题】：{user_question}

【回答】：
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1  # 设低一点 让回答更严谨 减少幻觉
    )
except Exception as e:
    print(f"LLM 调用失败: {e}")
    exit(1)

final_answer = response.choices[0].message.content
print(f"最终回答:\n{'-' * 30}\n{final_answer}")
