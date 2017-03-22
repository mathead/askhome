from datetime import datetime

from .utils import rstrip_word


def create_request(data, context=None):
    """Create a specific ``Request`` subclass according to the request type.

    Each ``Request`` subclass has specific properties to access request data more easily and differing
    ``response`` arguments for direct response creation.
    """
    name = data['header']['name']

    # Return Request subtype for specific requests
    if name == 'DiscoverAppliancesRequest':
        return DiscoverRequest(data, context)

    if name in ('IncrementPercentageRequest',
                'DecrementPercentageRequest',
                'SetPercentageRequest'):
        return PercentageRequest(data, context)

    if name in ('IncrementTargetTemperatureRequest',
                'DecrementTargetTemperatureRequest',
                'SetTargetTemperatureRequest'):
        return ChangeTemperatureRequest(data, context)

    if name == 'GetTargetTemperatureRequest':
        return GetTargetTemperatureRequest(data, context)

    if name == 'GetTemperatureReadingRequest':
        return TemperatureReadingRequest(data, context)

    if name in ('SetLockStateRequest', 'GetLockStateRequest'):
        return LockStateRequest(data, context)

    if name == 'HealthCheckRequest':
        return HealthCheckRequest(data, context)

    return Request(data, context)


class Request(object):
    """Base Request class for parsing Alexa request data.

    Attributes:
        data (dict): Raw event data from the lambda handler.
        context (object): Context object from the lambda handler.
        header (dict): Header of the Alexa request.
        payload (dict): Payload of the Alexa request.
        name (str): Request name from the ``name`` field in header.
        access_token (str): OAuth token from the ``accessToken`` field in payload.
        custom_data (Any): Attribute for saving custom data through
            ``Smarthome.prepare_request_handler``

    """
    def __init__(self, data, context=None):
        self.data = data
        self.context = context

        self.header = data['header']
        self.payload = data['payload']
        self.name = self.header['name']
        self.access_token = self.payload.get('accessToken', None)
        self.custom_data = None

    @property
    def appliance_id(self):
        """str: Identifier of the appliance from the appliance.applianceId of request payload."""
        if 'appliance' not in self.payload:
            return None
        return self.payload['appliance']['applianceId']

    @property
    def appliance_details(self):
        """dict: Information that was sent for the DiscoverApplianceRequest in field
        ``appliance.additionalApplianceDetails``
        """
        if 'appliance' not in self.payload:
            return None
        return self.payload['appliance']['additionalApplianceDetails']

    def response_header(self, name=None):
        """Generate response header with copied values from the request and correct name."""
        if name is None:
            # Figure out response name - Control requests have confirmations instead of responses
            name = rstrip_word(self.name, 'Request')
            if self.header['namespace'] == 'Alexa.ConnectedHome.Control':
                name += 'Confirmation'
            else:
                name += 'Response'

        # Copy request header and just change the name
        header = dict(self.header)
        header['name'] = name

        return header

    def raw_response(self, payload=None, header=None):
        """Compose response from raw payload and header dicts"""
        if payload is None:
            payload = {}
        if header is None:
            header = self.response_header()

        return {'header': header, 'payload': payload}

    def response(self, *args, **kwargs):
        """Return response with empty payload. Arguments and implementation of this method differ in
        each Request subclass.
        """
        return self.raw_response()

    def exception_response(self, exception):
        """Create response from exception instance."""
        # Use exception class name as response name
        header = self.response_header(exception.name)
        header['namespace'] = exception.namespace

        return {'header': header, 'payload': exception.payload}

    @staticmethod
    def _format_timestamp(timestamp):
        if isinstance(timestamp, datetime):
            # Format datetime according to documentation
            return timestamp.replace(microsecond=0).isoformat()
        else:
            return timestamp


class DiscoverRequest(Request):
    """Request class for Alexa DiscoverAppliancesRequest."""
    def response(self, smarthome):
        """Generate DiscoverAppliancesResponse from appliances added to the passed ``Smarthome``.

        Details of each appliance are resolved in order of priority:
        ``Smarthome.add_appliance`` kwargs -> ``Appliance.Details`` -> ``Smarthome.__init__`` kwargs
        """
        discovered = []
        for appl, details in smarthome.appliances.values():
            discovered.append(details)

        return self.raw_response({'discoveredAppliances': discovered})


class PercentageRequest(Request):
    """Request class for Alexa Increment/Decrement/SetPercentageRequest."""
    @property
    def percentage(self):
        if 'percentageState' not in self.payload:
            return None
        return self.payload['percentageState']['value']

    @property
    def delta_percentage(self):
        if 'deltaPercentage' not in self.payload:
            return None
        return self.payload['deltaPercentage']['value']


class ChangeTemperatureRequest(Request):
    """Request class for Alexa Increment/Decrement/SetTargetTemperatureRequest."""
    @property
    def temperature(self):
        if 'targetTemperature' not in self.payload:
            return None
        return self.payload['targetTemperature']['value']

    @property
    def delta_temperature(self):
        if 'deltaTemperature' not in self.payload:
            return None
        return self.payload['deltaTemperature']['value']

    def response(self, temperature, mode='AUTO', previous_temperature=None, previous_mode='AUTO'):
        """
        Args:
            temperature (float): Target temperature set by the device, in degrees Celsius.
            mode (str): Temperature mode of device. Can be 'AUTO', 'COOL' or 'HEAT'.
            previous_temperature (float): Previous target temperature in degrees Celsius.
            previous_mode (str): Previous temperature mode.
        """
        payload = {
            'targetTemperature': {
                "value": temperature
            },
            'temperatureMode': {
                'value': mode
            }
        }

        # Even though the docs say the previousState is required, it works fine without it
        if previous_temperature is not None:
            payload['previousState'] = {
                'targetTemperature': {
                    'value': previous_temperature
                },
                'mode': {
                    'value': previous_mode
                }
            }

        return self.raw_response(payload)


class GetTargetTemperatureRequest(Request):
    """Request class for Alexa GetTargetTemperatureRequest."""
    def response(self, temperature=None, cooling_temperature=None, heating_temperature=None,
                 mode='AUTO', mode_name=None, timestamp=None):
        """
        Args:
            temperature (float): Target temperature set by the device, in degrees Celsius.
            cooling_temperature (float): Target temperature (setpoint) for cooling, in degrees
                Celsius, when a device has dual setpoints. Usually combined with
                heatingTargetTemperature.
            heating_temperature (float): Target temperature (setpoint) for heating, in degrees
                Celsius, when a device has dual setpoints. Usually combined with
                coolingTargetTemperature.
            mode (str): Temperature mode of device. Can be one of 'AUTO', 'COOL', 'HEAT', 'ECO',
                'OFF', 'CUSTOM'.
            mode_name (str): Friendly name of the mode when it differs from the canonical name.
                Required when mode is 'CUSTOM'.
            timestamp (datetime|str): Time when the information was last retrieved.

        """
        payload = {
            'temperatureMode': {'value': mode}
        }

        if temperature is not None:
            payload['targetTemperature'] = {'value': temperature}
        if cooling_temperature is not None:
            payload['coolingTargetTemperature'] = {'value': cooling_temperature}
        if heating_temperature is not None:
            payload['heatingTargetTemperature'] = {'value': heating_temperature}
        if mode_name is not None:
            payload['temperatureMode']['friendlyName'] = mode_name
        # Add timestamp to payload if set
        if timestamp is not None:
            payload['applianceResponseTimestamp'] = self._format_timestamp(timestamp)

        return self.raw_response(payload)


class TemperatureReadingRequest(Request):
    """Request class for Alexa GetTemperatureReadingRequest."""
    def response(self, temperature, timestamp=None):
        """
        Args:
            temperature (float): Current temperature reading, in degrees Celsius.
            timestamp (datetime|str): Time when the information was last retrieved.
        """
        payload = {'temperatureReading': {'value': temperature}}
        # Add timestamp to payload if set
        if timestamp is not None:
            payload['applianceResponseTimestamp'] = self._format_timestamp(timestamp)
        return self.raw_response(payload)


class LockStateRequest(Request):
    """Request class for Alexa Get/SetLockStateRequest."""
    @property
    def lock_state(self):
        return self.payload['lockState']

    def response(self, lock_state, timestamp=None):
        """
        Args:
            lock_state (str): Can be 'LOCKED' or 'UNLOCKED' for GetLockStateRequest, can be only
                'LOCKED' for SetLockStateRequest (for security reasons).
            timestamp (datetime|str): Time when the information was last retrieved.
        """
        payload = {'lockState': lock_state}
        # Add timestamp to payload if set
        if timestamp is not None:
            payload['applianceResponseTimestamp'] = self._format_timestamp(timestamp)
        return self.raw_response(payload)


class HealthCheckRequest(Request):
    """Request class for Alexa HealthCheckRequest."""
    def response(self, healthy, description):
        return self.raw_response({
            'isHealthy': healthy,
            'description': description
        })
