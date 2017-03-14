from .utils import get_action_string, get_request_string, classproperty


class Appliance(object):
    def __init__(self, request=None):
        if request is not None:
            self.request = request
            self.id = request.appliance_id
            self.additional_details = request.appliance_details

    @classmethod
    def action(cls, func):
        last = getattr(func, 'ask_actions', [])
        func.ask_actions = last + [get_action_string(func.__name__)]
        cls.query(func)
        return func

    @classmethod
    def action_for(cls, *args):
        def decorator(func):
            last = getattr(func, 'ask_actions', [])
            func.ask_actions = last + map(get_action_string, args)
            cls.query_for(*args)(func)
            return func

        return decorator

    @classmethod
    def query(cls, func):
        last = getattr(func, 'ask_requests', [])
        func.ask_requests = last + [get_request_string(func.__name__)]
        return func

    @classmethod
    def query_for(cls, *args):
        def decorator(func):
            last = getattr(func, 'ask_requests', [])
            func.ask_requests = last + map(get_request_string, args)
            return func

        return decorator

    @classproperty
    @classmethod
    def actions(cls):
        ret = {}
        for method in cls.__dict__.values():
            for action in getattr(method, 'ask_actions', []):
                ret[action] = method

        return ret

    @classproperty
    @classmethod
    def request_handlers(cls):
        ret = {}
        for method in cls.__dict__.values():
            for action in getattr(method, 'ask_requests', []):
                ret[action] = method

        return ret
