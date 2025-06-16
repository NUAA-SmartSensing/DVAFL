from core.handlers.Handler import HandlerChain
from core.handlers.ModelTestHandler import ServerTestHandler, ServerPostTestHandler
from core.handlers.ServerHandler import Aggregation, GlobalModelOptimization, ClientUpdateGetter, UpdateCleanupHandler
from updater.BaseUpdater import BaseUpdater


class SyncUpdater(BaseUpdater):
    def __init__(self, server_thread_lock, config, mutex_sem, empty_sem, full_sem):
        BaseUpdater.__init__(self, server_thread_lock, config)
        self.mutex_sem = mutex_sem
        self.empty_sem = empty_sem
        self.full_sem = full_sem
        self.finals = []

    def _run_iteration(self) -> None:
        for _ in range(self.T):
            self.full_sem.acquire()
            self.mutex_sem.acquire()

            self.server_thread_lock.acquire()

            self.execute_chain()
            self.server_thread_lock.release()

            self.current_t.time_add()
            self.mutex_sem.release()
            self.empty_sem.release()

    def create_handler_chain(self):
        self.handler_chain = HandlerChain()
        (self.handler_chain.set_chain(ClientUpdateGetter())
         .set_next(Aggregation())
         .set_next(GlobalModelOptimization())
         .set_next(ServerTestHandler())
         .set_next(ServerPostTestHandler())
         .set_next(UpdateCleanupHandler()))

    def run_one_iteration(self) -> tuple:
        """执行一次更新迭代，用于顺序模拟

        无需获取信号量，因为在顺序模拟模式下不需要线程同步
        """
        self.server_thread_lock.acquire()
        requests = self.execute_chain()
        self.server_thread_lock.release()
        self.current_t.time_add()
        return self, requests

    def execute_chain(self):
        """执行更新处理链

        Returns:
            dict: 更新结果
        """
        epoch = self.current_t.get_time()
        request = {
            "epoch": epoch,
            "updater": self,
            "global_var": self.global_var,
            'scheduler': self.global_var['scheduler']
        }
        return self.handler_chain.handle(request)


class SyncUpdaterWithDetailedTest(SyncUpdater):
    def __init__(self, server_thread_lock, config, mutex_sem, empty_sem, full_sem):
        super().__init__(server_thread_lock, config, mutex_sem, empty_sem, full_sem)
        config['test'] = 'core.handlers.ModelTestHandler.TestEachClass'


class SyncUpdaterWithTaskTest(SyncUpdater):
    def __init__(self, server_thread_lock, config, mutex_sem, empty_sem, full_sem):
        super().__init__(server_thread_lock, config, mutex_sem, empty_sem, full_sem)
        config['test'] = 'core.handlers.ModelTestHandler.TestMultiTask'
