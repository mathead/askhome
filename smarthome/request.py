from datetime import datetime

from .utils import rstrip_word


class Request(object):
    def __init__(self, data, context=None):
        self.data = data
        self.context = context

        self.header = data['header']
        self.payload = data['payload']
        self.name = self.header['name']
        self.access_token = self.payload['accessToken']

    @property
    def appliance_id(self):
        if 'appliance' not in self.payload:
            return None
        return self.payload['appliance']['applianceId']

    @property
    def appliance_details(self):
        if 'appliance' not in self.payload:
            return None
        return self.payload['appliance']['additionalApplianceDetails']

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

    @property
    def lock_state(self):
        if 'lockState' not in self.payload:
            return None
        return self.payload['lockState']

    def response_header(self, name=None):
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

    @staticmethod
    def discover_payload(smarthome):
        discovered = []
        for appl_id, (appl, details) in smarthome.appliances:
            # Helper function to get detail in hierarchy:
            # Smarthome.add_device kwargs -> Appliance.Details -> Smarthome.__init__ kwargs
            def get_detail(name, default=''):
                if name in details:
                    return details[name]
                if hasattr(appl.Details, name):
                    return getattr(appl.Details, name)
                return smarthome.details.get(name, default)

            serialized = {
                'applianceId': appl_id,
                'manufacturerName': get_detail('manufacturer'),
                'modelName': get_detail('model'),
                'version': get_detail('version', '1'),
                'friendlyName': get_detail('name'),
                'friendlyDescription': get_detail('description'),
                'isReachable': get_detail('reachable', True),
                'additionalApplianceDetails': get_detail('additional_details', {}),
                'actions': sorted(appl.actions.values()),  # sorted for easier testing
            }
            discovered.append(serialized)

        return {'discoveredAppliance': discovered}

    @staticmethod
    def set_temperature_payload(temperature, mode='AUTO', previous_temperature=None, previous_mode='AUTO'):
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

        return payload

    @staticmethod
    def get_temperature_payload(temperature=None, cooling_temperature=None,
                                heating_temperature=None, mode='AUTO', mode_name=None):
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

        return payload

    @staticmethod
    def get_temperature_reading_payload(temperature):
        return {
            'temperatureReading': {'value': temperature}
        }

    @staticmethod
    def lock_state_payload(lock_state):
        return {'lockState': lock_state}

    @staticmethod
    def health_check_payload(healthy, description):
        return {
            'isHealthy': healthy,
            'description': description
        }

    def response(self, payload=None, timestamp=None, *args, **kwargs):
        if payload is not None:
            return {'header': self.response_header(), 'payload': payload}

        payload = {}

        if timestamp is not None:
            if isinstance(timestamp, datetime):
                # Format datetime according to documentation
                payload['applianceResponseTimestamp'] = timestamp.replace(microsecond=0).isoformat()
            else:
                payload['applianceResponseTimestamp'] = timestamp

        # Get payload from methods of specific requests
        if self.name == 'DiscoverAppliancesRequest':
            payload = self.discover_payload(*args, **kwargs)

        elif self.name in ('IncrementTargetTemperatureRequest',
                           'DecrementTargetTemperatureRequest',
                           'SetTargetTemperatureRequest'):
            payload = self.set_temperature_payload(*args, **kwargs)

        elif self.name == 'GetTargetTemperatureRequest':
            payload = self.get_temperature_payload(*args, **kwargs)

        elif self.name == 'GetTemperatureReadingRequest':
            payload = self.get_temperature_reading_payload(*args, **kwargs)

        return {'header': self.response_header(), 'payload': payload}
