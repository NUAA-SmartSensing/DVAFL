from receiver.NoneReceiver import NoneReceiver


class ReceiverCaller:
    def __init__(self, queue_manager):
        self.queue_manager = queue_manager

    def receive(self, queue, nums, *args, **kwargs):
        if isinstance(self.queue_manager.receiver, NoneReceiver):
            return self.queue_manager.receiver.receive()
        else:
            return self.queue_manager.receiver.receive(queue, nums, *args, **kwargs)

    def check_updates(self, update_num):
        if isinstance(self.queue_manager.receiver, NoneReceiver):
            return self.queue_manager.receiver.check()
        else:
            return self.queue_manager.receiver.check(self.queue_manager.queue, update_num)
