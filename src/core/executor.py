from concurrent.futures import ThreadPoolExecutor

# DB 操作
db_threadpool = ThreadPoolExecutor(max_workers=13, thread_name_prefix='db')

# 其他阻塞 IO
bio_threadpool = ThreadPoolExecutor(max_workers=5, thread_name_prefix='bio')

# Graph 执行（LLM 长任务，限制并发数防止资源耗尽）
graph_threadpool = ThreadPoolExecutor(max_workers=3, thread_name_prefix='graph')
