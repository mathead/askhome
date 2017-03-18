from .utils import get_action_string, get_request_string


class classproperty(property):
    """Utility class for @property fields on the class."""
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()


class Appliance(object):
    """Appliance subclasses are used to describe what actions devices support.

    Methods of subclasses can be marked with decorators (like `@Appliance.action`) and are used to
    generate Alexa DiscoverApplianceResponse. Alexa control and query requests are routed to the
    corresponding decorated method.

    Appliance subclass can also contain a `Details` inner class for instance defaults during
    discovery.

    Attributes:
        request (Request): Currently processed request.
        id (str): Identifier of the appliance from the appliance.applianceId of request payload.
        additional_details (dict): Information that was sent for the DiscoverApplianceRequest.
            Some instance specific details can be saved here.

    """

    def __init__(self, request=None):
        """Appliance gets initialized just before its query and action methods are called. Put your
        logic for preparation before handling the request here.
        """
        if request is not None:
            self.request = request
            self.id = request.appliance_id
            self.additional_details = request.appliance_details

    @classmethod
    def action(cls, func):
        """Decorator for marking the method as an action sent for the DiscoverApplianceRequest.

        The action name is generated from the camelCased method name (e. g. turn_on -> turnOn).
        The decorated method should take request as an argument, specific subclass of `Request` is
        passed for each action.

        Possible action methods and their corresponding `Request` types passed are:
            * turn_on(Request)
            * turn_off(Request)
            * set_percentage(PercentageRequest)
            * increment_percentage(PercentageRequest)
            * decrement_percentage(PercentageRequest)
            * set_target_temperature(ChangeTemperatureRequest)
            * increment_target_temperature(ChangeTemperatureRequest)
            * decrement_target_temperature(ChangeTemperatureRequest)
            * get_target_temperature(GetTemperatureRequest)
            * get_temperature_reading(TemperatureReadingRequest)
            * set_lock_state(LockStateRequest)
            * get_lock_state(LockStateRequest)

        """
        last = getattr(func, 'ask_actions', [])
        func.ask_actions = last + [get_action_string(func.__name__)]
        cls.query(func)
        return func

    @classmethod
    def action_for(cls, *args):
        """Decorator similar to the `action` decorator, except it doesn't generate the action name
        from the method name. All action names that should lead to the decorated method are passed
        as arguments to the decorator.
        """
        def decorator(func):
            last = getattr(func, 'ask_actions', [])
            func.ask_actions = last + map(get_action_string, args)
            cls.query_for(*args)(func)
            return func

        return decorator

    @classmethod
    def query(cls, func):
        """Decorator for marking the method to be routed to for its corresponding request.

        The action name is generated from the camelCased method name (e. g. turn_on -> turnOn).
        The decorated method should take request as an argument, specific subclass of `Request` is
        passed for each action.
        """
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

    class Details:
        """Some docs"""
