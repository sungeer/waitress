from concurrent.futures import ThreadPoolExecutor

# DB 操作
db_threadpool = ThreadPoolExecutor(max_workers=13, thread_name_prefix='db')

# 其他阻塞 IO
bio_threadpool = ThreadPoolExecutor(max_workers=5, thread_name_prefix='bio')
