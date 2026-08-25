from contextlib import suppress
from concurrent.futures import ThreadPoolExecutor


class _ExecutorPool:

    def __init__(self):
        self.db = None
        self.bio = None
        self.graph = None

    def init(self):
        self.db = ThreadPoolExecutor(max_workers=20, thread_name_prefix='db')
        self.bio = ThreadPoolExecutor(max_workers=8, thread_name_prefix='bio')

    def shutdown(self):
        if self.db:
            with suppress(Exception):
                self.db.shutdown(wait=True)
            self.db = None
        if self.bio:
            with suppress(Exception):
                self.bio.shutdown(wait=True)
            self.bio = None
        if self.graph:
            with suppress(Exception):
                self.graph.shutdown(wait=True)
            self.graph = None


executor = _ExecutorPool()
