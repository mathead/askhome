from smarthome.utils import get_action_string, classproperty


class Device(object):
    @classmethod
    def action(cls, func):
        func.ask_action = True
        return func

    @classmethod
    def action_for(cls, *args):
        def decorator(func):
            func.ask_action_for = args
            return func
        return decorator

    @classmethod
    def query(cls, func):
        func.ask_query = True
        return func

    @classmethod
    def query_for(cls, *args):
        def decorator(func):
            func.ask_query_for = args
            return func
        return decorator

    @classproperty
    @classmethod
    def actions(cls):
        ret = {}
        for name, method in cls.__dict__.iteritems():
            if hasattr(method, "ask_action"):
                ret[get_action_string(name)] = method
            if hasattr(method, "ask_action_for"):
                for action in method.ask_action_for:
                    ret[get_action_string(action)] = method
        return ret

    @classproperty
    @classmethod
    def queries(cls):
        return {
            get_action_string(name): method
            for name, method in cls.__dict__.iteritems()
            if hasattr(method, "ask_query")
        }
