from abc import abstractmethod


class AbstractReceiver:
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def receive(self, *args, **kwargs):
        pass

    @abstractmethod
    def check(self, *args, **kwargs):
        """检查队列中是否有足够的更新

        Args:
            *args: 可变参数
            **kwargs: 可变关键字参数

        Returns:
            bool: 是否有足够的更新
        """
        pass
