class SmartHomeException(Exception):
    namespace = 'Alexa.ConnectedHome.Control'
    
    def __init__(self, *args, **kwargs):
        # If payload was set in a subclass already, don't set it again
        if not hasattr(self, 'payload'):
            self.payload = {}
        if 'payload' in kwargs:
            self.payload = kwargs.pop('payload')

        # Name in request header is same as class name
        self.name = type(self).__name__
        if 'name' in kwargs:
            self.name = kwargs.pop('name')

        super(SmartHomeException, self).__init__(*args, **kwargs)


class ValueOutOfRangeError(SmartHomeException):
    def __init__(self, min_val, max_val, *args, **kwargs):
        self.payload = {
            'minimumValue': min_val,
            'maximumValue': max_val
        }
        super(ValueOutOfRangeError, self).__init__(*args, **kwargs)


class TargetOfflineError(SmartHomeException):
    pass


class NoSuchTargetError(SmartHomeException):
    pass


class BridgeOfflineError(SmartHomeException):
    pass


class DriverInternalError(SmartHomeException):
    pass


class DependentServiceUnavailableError(SmartHomeException):
    def __init__(self, service_name, *args, **kwargs):
        self.payload = {'dependentServiceName': service_name}
        super(DependentServiceUnavailableError, self).__init__(*args, **kwargs)


class TargetConnectivityUnstableError(SmartHomeException):
    pass


class TargetBridgeConnectivityUnstableError(SmartHomeException):
    pass


class TargetFirmwareOutdatedError(SmartHomeException):
    def __init__(self, min_version, cur_version, *args, **kwargs):
        self.payload = {
            'minimumFirmwareVersion': min_version,
            'currentFirmwareVersion': cur_version
        }
        super(TargetFirmwareOutdatedError, self).__init__(*args, **kwargs)


class TargetBridgeFirmwareOutdatedError(SmartHomeException):
    def __init__(self, min_version, cur_version, *args, **kwargs):
        self.payload = {
            'minimumFirmwareVersion': min_version,
            'currentFirmwareVersion': cur_version
        }
        super(TargetBridgeFirmwareOutdatedError, self).__init__(*args, **kwargs)


class TargetHardwareMalfunctionError(SmartHomeException):
    pass


class TargetBridgeHardwareMalfunctionError(SmartHomeException):
    pass


class UnableToGetValueError(SmartHomeException):
    namespace = 'Alexa.ConnectedHome.Query'

    def __init__(self, error_code, error_description=None, *args, **kwargs):
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnableToGetValueError, self).__init__(*args, **kwargs)


class UnableToSetValueError(SmartHomeException):
    def __init__(self, error_code, error_description=None, *args, **kwargs):
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnableToSetValueError, self).__init__(*args, **kwargs)


class UnwillingToSetValueError(SmartHomeException):
    def __init__(self, error_code='ThermostatIsOff', error_description=None, *args, **kwargs):
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnwillingToSetValueError, self).__init__(*args, **kwargs)


class RateLimitExceededError(SmartHomeException):
    def __init__(self, rate_limit, time_unit='HOUR', *args, **kwargs):
        self.payload = {
            'rateLimit': rate_limit,
            'timeUnit': time_unit
        }
        super(RateLimitExceededError, self).__init__(*args, **kwargs)


class NotSupportedInCurrentModeError(SmartHomeException):
    def __init__(self, current_mode, *args, **kwargs):
        self.payload = {'currentDeviceMode': current_mode}
        super(NotSupportedInCurrentModeError, self).__init__(*args, **kwargs)


class ExpiredAccessTokenError(SmartHomeException):
    pass


class InvalidAccessTokenError(SmartHomeException):
    pass


class UnsupportedTargetError(SmartHomeException):
    pass


class UnsupportedOperationError(SmartHomeException):
    pass


class UnsupportedTargetSettingError(SmartHomeException):
    pass


class UnexpectedInformationReceivedError(SmartHomeException):
    def __init__(self, faulting_parameter, *args, **kwargs):
        self.payload = {'faultingParameter': faulting_parameter}
        super(UnexpectedInformationReceivedError, self).__init__(*args, **kwargs)
