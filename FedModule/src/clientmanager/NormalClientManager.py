from clientmanager.BaseClientManager import BaseClientManager
from clientmanager.ClientFactroy import ClientFactory
from core.MessageQueue import EventFactory
from utils import ModuleFindTool
from utils.GlobalVarGetter import GlobalVarGetter


class NormalClientManager(BaseClientManager):
    def __init__(self, whole_config):
        super().__init__(whole_config)
        self.global_var = GlobalVarGetter.get()
        self.client_list = []  # client list
        self.client_id_list = []  # client id list

        config = whole_config["client_manager"]
        self.multi_gpu = whole_config["global"]["multi_gpu"]
        self.total_client_num = whole_config["global"]["client_num"]
        self.client_num = self.total_client_num
        self.client_staleness_list = config["stale_list"]
        self.index_list = config["index_list"]  # each client's index list
        self.client_config = whole_config["client"]
        self.client_events = config.get("client_events", [])
        self.client_dev = self.get_client_dev_list(self.total_client_num, self.multi_gpu)
        self.client_factory = ModuleFindTool.find_class_by_path(
            config['client_factory']['path']) if 'client_factory' in config else ClientFactory
        # 记录所有已创建的client
        self.all_client_ids = set()
        # 记录当前活跃client
        self.client_id_list = []
        # 记录初始激活的client id（未被client_events join控制的）
        self.initial_active_ids = self._get_initial_active_ids()
        self.stop_event_list = [EventFactory.create_Event() for _ in range(self.total_client_num)]
        self.selected_event_list = [EventFactory.create_Event() for _ in range(self.total_client_num)]
        self.global_var['selected_event_list'] = self.selected_event_list

    def _get_initial_active_ids(self):
        # 统计所有join事件涉及的id
        join_ids = set()
        for event in self.client_events:
            join_ids.update(event.get('join', []))
        # 初始激活id为[0, total_client_num)中未被join事件控制的id
        return [i for i in range(self.total_client_num) if i not in join_ids]

    def __init_clients(self):
        # 只初始化初始激活的client
        self.client_id_list = list(self.initial_active_ids)
        self.client_list = [None] * self.total_client_num
        for cid in self.client_id_list:
            self._create_client(cid)

    def _create_client(self, client_id):
        # 创建单个client实例，使用统一接口
        self.client_list[client_id] = self.client_factory.create_client(
            client_id, self.stop_event_list[client_id],
            self.selected_event_list[client_id],
            self.client_staleness_list[client_id], self.index_list[client_id],
            self.client_config, self.client_dev[client_id], self.global_var['config'])
        self.all_client_ids.add(client_id)

    def create_and_start_new_client(self, client_id=None, dev=None):
        # 支持指定client_id创建
        if client_id is None:
            client_id = len(self.client_id_list)
        if self.client_list[client_id] is None:
            self._create_client(client_id)
        if client_id not in self.client_id_list:
            self.client_id_list.append(client_id)
        self.client_list[client_id].start()

    def update_active_clients(self, current_round):
        # 根据client_events动态join/leave
        for event in self.client_events:
            if event.get('round') == current_round:
                # join
                for cid in event.get('join', []):
                    if self.client_list[cid] is None:
                        self._create_client(cid)
                    if cid not in self.client_id_list:
                        self.client_id_list.append(cid)
                        self.client_list[cid].start()
                # leave
                for cid in event.get('leave', []):
                    if cid in self.client_id_list:
                        self.stop_client_by_id(cid)
                        self.client_id_list.remove(cid)

    def start_all_clients(self):
        self.__init_clients()
        # 启动初始client
        self.global_var['client_list'] = self.client_list
        self.global_var['client_id_list'] = self.client_id_list
        print("Starting clients")
        for i in self.client_id_list:
            self.client_list[i].start()

    def get_client_list(self):
        return self.client_list

    def get_client_id_list(self):
        return self.client_id_list

    def stop_all_clients(self):
        # stop all clients
        for i in self.client_id_list:
            self.stop_client_by_id(i)

    def stop_client_by_id(self, client_id):
        self.stop_event_list[client_id].set()
        self.selected_event_list[client_id].set()

    def client_join(self):
        for i in self.client_list:
            i.join()
