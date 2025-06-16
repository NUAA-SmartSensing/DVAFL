"""
集中存放DataStore自定义存储策略，并提供统一注册接口。
"""


def model_get_func(client_id, key, default=None, data_store=None):
    """
    只返回模型的可训练参数。
    从data_store.clients获取client实例。
    """
    client = None
    if data_store is not None and hasattr(data_store, 'clients'):
        client = data_store.clients.get(client_id, None)
    if client is None:
        return default
    model = getattr(client, 'model', None)
    if model is None:
        return default
    # 只返回可训练参数
    return {k: v for k, v in model.state_dict().items() if getattr(model.state_dict()[k], 'requires_grad', True)}


def model_set_func(client_id, key, value, data_store=None):
    """
    只设置模型的可训练参数。
    优先从data_store.clients获取client实例。
    """
    client = None
    if data_store is not None and hasattr(data_store, 'clients'):
        client = data_store.clients.get(client_id, None)
    if client is None:
        return
    model = getattr(client, 'model', None)
    if model is None:
        return
    state_dict = model.state_dict()
    for k, v in value.items():
        if k in state_dict and getattr(state_dict[k], 'requires_grad', True):
            state_dict[k].copy_(v)
    model.load_state_dict(state_dict, strict=False)


# 全局注册表
DATASTORE_STRATEGY_REGISTRY = []


def datastore_strategy_register(func):
    """
    装饰器：将注册函数加入全局注册表
    """
    DATASTORE_STRATEGY_REGISTRY.append(func)
    return func


# 用装饰器注册策略
@datastore_strategy_register
def register_model_strategy(data_store):
    data_store.register_strategy(
        'model',
        get_func=model_get_func,
        set_func=model_set_func
    )
