import torch

from core.handlers.Handler import Handler
from utils.Tools import to_dev, to_cpu


class ClientUpdateGetter(Handler):
    """更新获取处理程序"""

    def _handle(self, request):
        update_list = []
        global_var = request.get('global_var')
        queue_manager = global_var['queue_manager']
        # receive all updates
        while not queue_manager.empty():
            update_list.append(queue_manager.get())
        request['update_list'] = update_list
        return request


class Aggregation(Handler):
    """聚合处理程序"""

    def _handle(self, request):
        update_list = request.get('update_list')
        updater = request.get('updater')
        epoch = request.get('epoch')
        global_model, delivery_weights = updater.update_caller.update_server_weights(epoch, update_list)
        request['weights'] = global_model
        request['delivery_weights'] = delivery_weights
        global_var = request.get('global_var')
        global_var['delivery_weights'] = delivery_weights
        return request


class GlobalModelOptimization(Handler):
    """全局模型优化处理程序"""

    def _handle(self, request):
        optim = request.get('optim')
        global_var = request.get('global_var')
        global_model = request.get('weights')
        updater = request.get('updater')

        new_model = to_dev(global_model, 'cuda')
        if optim is not None:
            training_params = global_var['training_params']
            old_model = updater.model.state_dict()
            g = {}
            for k in new_model:
                if training_params[k]:
                    g[k] = new_model[k] - old_model[k]
            for k, w in zip(g, updater.model.parameters()):
                w.grad = -g[k]
            optim.step()
        else:
            updater.model.load_state_dict(new_model)
        request['weights'] = to_cpu(updater.model.state_dict())
        return request


class UpdateActiveClientsHandler(Handler):
    """用于每轮训练前动态更新活跃客户端列表的Handler"""
    def _handle(self, request):
        global_var = request.get('global_var')
        epoch = request.get('epoch')
        scheduler = global_var.get('scheduler')

        if 'client_manager' in global_var:
            client_manager = global_var['client_manager']
            # 调用client_manager的update_active_clients方法处理加入/退出事件
            if hasattr(client_manager, 'update_active_clients'):
                client_manager.update_active_clients(epoch)
            # 同步最新的client_id_list到global_var
            global_var['client_id_list'] = client_manager.get_client_id_list()
        return request


class ClientSelector(Handler):
    def _handle(self, request):
        global_var = request.get('global_var')
        scheduler = global_var['scheduler']
        epoch = request.get('epoch')
        if hasattr(scheduler, 'client_select'):
            selected_clients = scheduler.client_select()
        else:
            client_list = global_var['client_id_list']
            training_status = scheduler.message_queue.get_training_status()
            client_list = [client_id for client_id in client_list if
                           client_id not in training_status or not training_status[client_id]]
            selected_clients = scheduler.schedule_caller.schedule(client_list)
        request['selected_clients'] = selected_clients
        global_var['selected_clients'] = selected_clients
        print(f"| current_epoch {epoch}, schedule_epoch {scheduler.schedule_t.get_time()} |")
        print("selected_clients:", selected_clients)
        return request


class ContentDispatcher(Handler):
    def _handle(self, request):
        scheduler = request.get('scheduler')
        self.handle_weights(request, scheduler)
        self.handle_download(request, scheduler)
        scheduler.notify_client()
        self.handle_selected_event(request, scheduler)
        return request

    @staticmethod
    def handle_weights(request, scheduler):
        global_var = request.get('global_var')
        selected_clients = request['selected_clients']
        delivery_weights = global_var['delivery_weights']
        updater = global_var['updater']
        weights = request.get('weights', updater.model.state_dict())
        if delivery_weights is not None and len(delivery_weights) > 0:
            for client_id in selected_clients:
                if client_id in delivery_weights:
                    scheduler.download_item(client_id, 'weights', delivery_weights[client_id])
                else:
                    scheduler.download_item(client_id, 'weights', weights)
        else:
            for client_id in selected_clients:
                scheduler.download_item(client_id, 'weights', weights)

    @staticmethod
    def handle_selected_event(request, scheduler):
        selected_clients = request.get('selected_clients')
        for client_id in selected_clients:
            scheduler.selected_event_list[client_id].set()

    @staticmethod
    def handle_download(request, scheduler):
        current_time = scheduler.current_t.get_time()
        schedule_time = scheduler.schedule_t.get_time()
        scheduler.download_item('all', 'time_stamp', current_time)
        scheduler.download_item('all', 'schedule_time_stamp', schedule_time)


class UpdateWaiter(Handler):
    def _handle(self, request):
        scheduler = request.get('scheduler')
        global_var = request.get('global_var', {})

        # 获取更新数量
        update_num = request.get('update_num', len(request.get('selected_clients', [])))

        # 检查是否为顺序模拟模式
        if global_var.get('config', {}).get('global', {}).get('sequential_mode', False):
            # 在顺序模拟模式下，只检查状态而不等待
            if hasattr(scheduler, 'check_updates'):
                result = scheduler.check_updates(update_num)
            else:
                result = scheduler.queue_manager.check_updates(update_num)
            request['updates_ready'] = result
        else:
            # 非顺序模拟模式，使用原有的等待逻辑
            if hasattr(scheduler, 'wait'):
                scheduler.wait()
            else:
                scheduler.queue_manager.receive(update_num)
            request['updates_ready'] = True

        return request


class UpdateCleanupHandler(Handler):
    """专门处理request内显存和内存占用问题的Handler"""
    def _handle(self, request):
        update_list = request.get('update_list', [])
        # 清空 update_list
        update_list.clear()
        torch.cuda.empty_cache()
        return request
