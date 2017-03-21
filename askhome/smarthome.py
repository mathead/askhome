import json

from .exceptions import AskhomeException, UnsupportedTargetError, UnsupportedOperationError
from .requests import create_request
from . import logger


class Smarthome(object):
    """Holds information about all appliances and handles routing requests to appliance actions.

    Attributes:
        appliances (dict(str, (Appliance, dict))): All registered appliances with details dict.
        details (dict): Defaults for details of appliances during DiscoverAppliancesRequest.

    """
    def __init__(self, **details):
        """
        Args:
            details (dict): Defaults for details of appliances during DiscoverAppliancesRequest.
                See ``add_appliance`` method for possible values.
        """
        self.appliances = {}
        self.details = details
        self._discover_func = None
        self._get_appliance_func = None
        self._healthcheck_func = None

    def add_appliance(self, appl_id, appl_class, name=None, description=None,
                      additional_details=None, model=None, version=None, manufacturer=None,
                      reachable=None):
        """Register ``Appliance`` so it can be discovered and routed to.

        The keyword arguments can be also defined in ``Smarthome.__init__`` and ``Details`` inner
        class in the appliance. Resulting value is resolved in order of priority:
        ``Smarthome.add_device`` kwargs -> ``Appliance.Details`` -> ``Smarthome.__init__`` kwargs

        Args:
            appl_id (str): Unique identifier of the appliance, needs to be consistent across
                multiple discovery requests for the same device. Can contain any letter or number
                and the following special characters: _ - = # ; : ? @ &. Cannot exceed 256
                characters.
            appl_class (Appliance): ``Appliance`` subclass with marked actions.
            name (str): Friendly name used by the customer to identify the device. Cannot exceed 128
                characters and should not contain special characters or punctuation.
            description (str): Human-readable description of the device. This value cannot exceed
                128 characters. The description should contain a description of how the device is
                connected. For example, "WiFi Thermostat connected via Wink".
            additional_details (dict(str, str)): Some instance specific details can be saved here.
                This field is sent back every time a request on that appliance is made. Cannot
                exceed 5000 bytes.
            model (str): Device model name. Cannot exceed 128 characters.
            version (str): Vendor-provided version of the device. Cannot exceed 128 characters.
            manufacturer (str): Name of device manufacturer. Cannot exceed 128 characters.
            reachable (bool): Indicate if device is currently reachable.

        """
        # The kwargs are explicitly named for better autocomplete

        # Helper function to get detail in hierarchy:
        # Smarthome.add_device kwargs -> Appliance.Details -> Smarthome.__init__ kwargs
        def get_detail(detail_name, arg, default=''):
            if arg is not None:
                return arg
            if hasattr(appl_class, 'Details') and hasattr(appl_class.Details, detail_name):
                return getattr(appl_class.Details, detail_name)
            return self.details.get(detail_name, default)

        details = {
            'applianceId': appl_id,
            'friendlyName': get_detail('name', name),
            'friendlyDescription': get_detail('description', description, 'No description'),
            'additionalApplianceDetails': get_detail('additional_details', additional_details, {}),
            'modelName': get_detail('model', model,  'Unknown model'),
            'version': get_detail('version', version, 'v1'),
            'manufacturerName': get_detail('manufacturer', manufacturer, 'Unknown manufacturer'),
            'isReachable': get_detail('reachable', reachable, True),
            'actions': sorted(appl_class.actions.keys()),  # sorted for easier testing
        }
        self.appliances[appl_id] = (appl_class, details)

    def discover_handler(self, func):
        """Decorator for a function that handles the DiscoverAppliancesRequest instead of the
        ``Smarthome``. This can be useful for situations where querying the list of all devices
        is too expensive to be done every request. Should be used in conjunction with the
        ``get_appliance_handler`` decorator.
        """
        self._discover_func = func
        return func

    def get_appliance_handler(self, func):
        """Decorator for a function that handles getting the ``Appliance`` subclass instead of the
        ``Smarthome``. Should be used in conjunction with the ``get_appliance_handler`` decorator.
        """
        self._get_appliance_func = func
        return func

    def healthcheck_handler(self, func):
        """Decorator for a function that handles ``HealthCheckRequest``. Behaves the same as a
        regular action method.
        """
        self._healthcheck_func = func
        return func

    def lambda_handler(self, data, context=None):
        """Main entry point for handling requests. Pass the AWS Lambda events here."""
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

            # Handle health check
            if request.name == "HealthCheckRequest":
                if self._healthcheck_func is None:
                    return request.response(healthy=True, description="Everything's OK")
                return self._healthcheck_func(request)

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
            response = request.exception_response(exception)
            logger.info('Exception raised: %r, %s', exception, response)
            return response
