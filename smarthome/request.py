class Request(object):
    def __init__(self, data, context=None):
        self.data = data
        self.context = context

        self.header = data['header']
        self.payload = data['payload']
        self.name = self.header['name']
        self.access_token = self.payload['accessToken']

    @property
    def appliance(self):
        if 'appliance' not in self.payload:
            return None

        appliance = self.payload['appliance']
        return _Bunch(
            id=appliance['applianceId'],
            additional_details=appliance['additionalApplianceDetails']
        )

    @property
    def percentage(self):
        if 'percentageState' not in self.payload and 'deltaPercentage' not in self.payload:
            return None

        return _Bunch(
            value=self.payload['percentageState'].get('value', None),
            delta=self.payload['deltaPercentage'].get('value', None)
        )

    @property
    def temperature(self):
        if 'targetTemperature' not in self.payload and 'deltaTemperature' not in self.payload:
            return None

        return _Bunch(
            target=self.payload['targetTemperature'].get('value', None),
            delta=self.payload['deltaTemperature'].get('value', None)
        )

    @property
    def lock(self):
        if 'lockState' not in self.payload:
            return None

        return _Bunch(state=self.payload['lockState'])


class _Bunch:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)