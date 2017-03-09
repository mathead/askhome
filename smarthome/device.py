class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()

class Device(object):
    @classmethod
    def action(cls, func):
        # cls.controls[func.__name__] = func
        func.ask_action = True
        return func

    @classproperty
    @classmethod
    def actions(cls):
        return {name: method for name, method in cls.__dict__.iteritems() if hasattr(method, "ask_action")}