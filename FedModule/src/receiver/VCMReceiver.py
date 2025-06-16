from time import sleep

from receiver.AbstractReceiver import AbstractReceiver


class VCMReceiver(AbstractReceiver):
    def __init__(self, config):
        super().__init__(config)

    def receive(self, queue_manager, nums):
        while not self.check(queue_manager, nums):
            sleep(0.01)

    def check(self, queue_manager, nums):
        """检查队列管理器中是否有足够的更新

        Args:
            queue_manager: 消息队列管理器
            nums: 需要的更新数量

        Returns:
            bool: 是否有足够的更新
        """
        return queue_manager.client_num >= nums
