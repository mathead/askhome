import json

from .exceptions import AskhomeException, UnsupportedTargetError, UnsupportedOperationError
from .requests import create_request
from . import logger


class Smarthome(object):
    def __init__(self, **kwargs):
        self.appliances = {}
        self.details = kwargs
        self._discover_func = None
        self._get_appliance_func = None

    def discover_handler(self, func):
        self._discover_func = func
        return func

    def get_appliance_handler(self, func):
        self._get_appliance_func = func
        return func

    def add_appliance(self, appl_id, appl_class, **details):
        self.appliances[appl_id] = (appl_class, details)

    def lambda_handler(self, data, context=None):
        logger.debug(json.dumps(data, indent=2))

        response = self._lambda_handler(data, context)
        logger.debug(json.dumps(response, indent=2))
        return response

    def _lambda_handler(self, data, context=None):
        # This method is here just so it can be wrapped for logging
        request = create_request(data, context)

        try:
            # Handle discover request
            if request.name == 'DiscoverAppliancesRequest':
                if self._discover_func is None:
                    return request.response(self)
                return self._discover_func(request)

            # Find the according appliance
            if self._get_appliance_func is None:
                # Appliance not found - return error response
                if request.appliance_id not in self.appliances:
                    raise UnsupportedTargetError
                appliance_cls = self.appliances[request.appliance_id][0]
            else:
                appliance_cls = self._get_appliance_func(request)

            # Appliance doesn't handle requested operation - return error response
            if request.name not in appliance_cls.request_handlers:
                raise UnsupportedOperationError

            # Finally instantiate the appliance and call the requested method
            appliance = appliance_cls(request)
            response = appliance_cls.request_handlers[request.name](appliance, request)

            if response is None:
                return request.response()
            return response

        except AskhomeException as exception:
            return request.exception_response(exception)
