from .utils import get_action_string, get_request_string


class _classproperty(property):
    """Utility class for @property fields on the class."""
    def __init__(self, func):
        self.func = func
        self.__doc__ = func.__doc__

    def __get__(self, instance, owner):
        # This makes docstrings work
        if owner is Appliance:
            return self
        return self.func(owner)


class Appliance(object):
    """Appliance subclasses are used to describe what actions devices support.

    Methods of subclasses can be marked with decorators (like ``@Appliance.action``) and are used to
    generate the Alexa DiscoverApplianceResponse. Alexa control and query requests are then routed
    to the corresponding decorated method.

    Appliance subclass can also contain a ``Details`` inner class for instance defaults during
    discovery (see ``Smarthome.add_appliance`` for possible attributes).

    Attributes:
        request (Request): Currently processed request.
        id (str): Identifier of the appliance from the appliance.applianceId of request payload.
        additional_details (dict): Information that was sent for the DiscoverAppliancesRequest.
            Some instance specific details can be saved here.

    """

    def __init__(self, request=None):
        """Appliance gets initialized just before its action methods are called. Put your
        logic for preparation before handling the request here.
        """
        if request is not None:
            self.request = request
            self.id = request.appliance_id
            self.additional_details = request.appliance_details

    @classmethod
    def action(cls, func):
        """Decorator for marking the method as an action sent for the DiscoverAppliancesRequest.

        The action name is generated from the camelCased method name (e.g. turn_on -> turnOn).
        The decorated method should take request as an argument, specific subclass of ``Request`` is
        passed for each action.

        Possible action methods and their corresponding ``Request`` types passed are:
            * turn_on(:class:`askhome.requests.Request`)
            * turn_off(:class:`askhome.requests.Request`)
            * set_percentage(:class:`askhome.requests.PercentageRequest`)
            * increment_percentage(:class:`askhome.requests.PercentageRequest`)
            * decrement_percentage(:class:`askhome.requests.PercentageRequest`)
            * set_target_temperature(:class:`askhome.requests.ChangeTemperatureRequest`)
            * increment_target_temperature(:class:`askhome.requests.ChangeTemperatureRequest`)
            * decrement_target_temperature(:class:`askhome.requests.ChangeTemperatureRequest`)
            * get_target_temperature(:class:`askhome.requests.GetTargetTemperatureRequest`)
            * get_temperature_reading(:class:`askhome.requests.TemperatureReadingRequest`)
            * set_lock_state(:class:`askhome.requests.LockStateRequest`)
            * get_lock_state(:class:`askhome.requests.LockStateRequest`)

        """
        last = getattr(func, 'ask_actions', [])
        func.ask_actions = last + [func.__name__]
        return func

    @classmethod
    def action_for(cls, *args):
        """Decorator similar to the ``action`` decorator, except it doesn't generate the action name
        from the method name. All action names that should lead to the decorated method are passed
        as arguments to the decorator.
        """
        def decorator(func):
            last = getattr(func, 'ask_actions', [])
            func.ask_actions = last + list(args)
            return func

        return decorator

    @_classproperty
    def actions(cls):
        """dict(str, function): All actions the appliance supports and their corresponding (unbound)
        method references. Action names are formatted for the DiscoverAppliancesRequest.
        """
        ret = {}
        for method in cls.__dict__.values():
            for action in getattr(method, 'ask_actions', []):
                ret[get_action_string(action)] = method

        return ret

    @_classproperty
    def request_handlers(cls):
        """dict(str, function): All requests the appliance supports (methods marked as actions)
        and their corresponding (unbound) method references. For example action turn_on would be
        formatted as TurnOnRequest.
        """
        ret = {}
        for method in cls.__dict__.values():
            for action in getattr(method, 'ask_actions', []):
                ret[get_request_string(action)] = method

        return ret

    class Details:
        """Inner class in ``Appliance`` subclasses provides default values so that they don't
        have to be repeated in ``Smarthome.add_appliance``.
        """
