import time

from core.handlers.Handler import HandlerChain
from core.handlers.ServerHandler import ClientSelector, ContentDispatcher, UpdateWaiter
from scheduler.BaseScheduler import BaseScheduler


class SyncScheduler(BaseScheduler):
    def __init__(self, server_thread_lock, config, mutex_sem, empty_sem, full_sem):
        BaseScheduler.__init__(self, server_thread_lock, config)
        self.mutex_sem = mutex_sem
        self.empty_sem = empty_sem
        self.full_sem = full_sem
        self.finals = []

    def _run_iteration(self) -> None:
        while self.current_t.get_time() <= self.T:
            # Scheduling is performed periodically.
            self.empty_sem.acquire()
            self.mutex_sem.acquire()
            self.run_one_iteration()
            # 通知更新器进行权重聚合
            self.mutex_sem.release()
            self.full_sem.release()
            time.sleep(0.01)

    def run_one_iteration(self) -> tuple:
        """执行一次调度迭代

        Returns:
            dict: 调度结果
        """
        result = self.execute_chain()
        self.schedule_t.time_add()
        return self, result

    def create_handler_chain(self):
        self.handler_chain = HandlerChain()
        (self.handler_chain.set_chain(ClientSelector())
         .set_next(ContentDispatcher())
         .set_next(UpdateWaiter()))

    def execute_chain(self):
        """执行调度处理链，并返回结果"""
        epoch = self.current_t.get_time()
        request = {
            "epoch": epoch,
            "updater": self,
            "global_var": self.global_var,
            'scheduler': self.global_var['scheduler']
        }
        return self.handler_chain.handle(request)
