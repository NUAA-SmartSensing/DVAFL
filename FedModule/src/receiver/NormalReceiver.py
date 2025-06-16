import time

from receiver.AbstractReceiver import AbstractReceiver


class NormalReceiver(AbstractReceiver):
    def __init__(self, config):
        super().__init__(config)

    # to support any queue_manger
    def receive(self, queue, nums):
        while not self.check(queue, nums):
            time.sleep(0.01)

    def check(self, queue, nums):
        """检查队列中是否有足够的更新

        Args:
            queue: 消息队列
            nums: 需要的更新数量

        Returns:
            bool: 是否有足够的更新
        """
        return queue.qsize() >= nums
