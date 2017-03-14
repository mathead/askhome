from .exceptions import SmartHomeException
from .request import Request


class Smarthome(object):
    def __init__(self, **kwargs):
        self.appliances = {}
        self.details = kwargs
        self._discover_func = None
        self._get_appliance_func = None

    def discover(self, func):
        self._discover_func = func
        return func

    def get_appliance(self, func):
        self._get_appliance_func = func
        return func

    def add_appliance(self, appl_id, appl_class, **details):
        self.appliances[appl_id] = (appl_class, details)

    def lambda_handler(self, data, context=None):
        request = Request(data, context)

        try:
            if request.name == 'DiscoverAppliancesRequest':
                if self._discover_func is None:
                    return request.response(self)
                return self._discover_func(request)

            # TODO raise
            if self._get_appliance_func is None:
                appliance = self.appliances[request.appliance_id][0](request)
            else:
                appliance = self._get_appliance_func(request)

            # TODO raise
            response = appliance.request_handlers[request.name](appliance, request)
            if response is None:
                return request.response()
            return response

        except SmartHomeException as exception:
            return request.exception_response(exception)
