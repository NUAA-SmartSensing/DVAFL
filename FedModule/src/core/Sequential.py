from core.Runtime import Mode


class Sequential(Mode):
    """
    Sequential is a class that simulates the running mode of the client in a sequential manner.
    It inherits from Mode and implements the run method to execute the client's run_one_iteration method.
    """
    def __init__(self, client):
        super().__init__(client)

    def join(self):
        pass

    def start(self):
        pass

    def run(self):
        return self.client.run_one_iteration()
