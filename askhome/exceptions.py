class AskhomeException(Exception):
    """Base askhome exception from which all inherit.

    These exceptions can be raised in ``Appliance`` actions or manually passed to
    ``Request.exception_response`` to create an error response.
    """
    namespace = 'Alexa.ConnectedHome.Control'
    
    def __init__(self, *args, **kwargs):
        """
        Args:
            name (str): Custom error name in header of generated response
            payload (dict): Custom payload of generated response
        """
        # If payload was set in a subclass already, don't set it again
        if not hasattr(self, 'payload'):
            self.payload = {}
        if 'payload' in kwargs:
            self.payload = kwargs.pop('payload')

        # Name in request header is same as class name
        self.name = type(self).__name__
        if 'name' in kwargs:
            self.name = kwargs.pop('name')

        super(AskhomeException, self).__init__(*args, **kwargs)


# All following exception docstrings are taken directly from:
# https://developer.amazon.com/public/solutions/alexa/alexa-skills-kit/docs/smart-home-skill-api-reference

# User Faults

class ValueOutOfRangeError(AskhomeException):
    """Amazon docs: Indicates a customer request would set a target value to a value out of its
    supported range. For example, a customer asks, "Alexa, set the kitchen to 1000 degrees".
    """
    def __init__(self, min_val, max_val, *args, **kwargs):
        self.payload = {
            'minimumValue': min_val,
            'maximumValue': max_val
        }
        super(ValueOutOfRangeError, self).__init__(*args, **kwargs)


class TargetOfflineError(AskhomeException):
    """Amazon docs: Indicates that the target device is not connected to the customer's device
    cloud or is not on.
    """


class NoSuchTargetError(AskhomeException):
    """Amazon docs: Indicates that the target device cannot be found, meaning it was never
    configured by the end-user.
    """


class BridgeOfflineError(AskhomeException):
    """Amazon docs: Indicates the target device is connected to a home automation hub or bridge,
    which is powered off.
    """


# Skill Adapter Faults

class DriverInternalError(AskhomeException):
    """Amazon docs: Indicates a generic runtime error within the skill adapter. When possible,
    a more specific error should be returned.
    """


class DependentServiceUnavailableError(AskhomeException):
    """Amazon docs: Indicates that a skill adapter dependency is unavailable and the skill adapter
    cannot complete the request.
    """
    def __init__(self, service_name, *args, **kwargs):
        self.payload = {'dependentServiceName': service_name}
        super(DependentServiceUnavailableError, self).__init__(*args, **kwargs)


class TargetConnectivityUnstableError(AskhomeException):
    """Amazon docs: Indicates the cloud-connectivity for the target device is not stable and
    reliable.
    """


class TargetBridgeConnectivityUnstableError(AskhomeException):
    """Amazon docs: Indicates that cloud-connectivity for a home automation hub or bridge that
    connects the target device is unstable and unreliable.
    """


class TargetFirmwareOutdatedError(AskhomeException):
    """Amazon docs: Indicates that the target device has outdated firmware."""
    def __init__(self, min_version, cur_version, *args, **kwargs):
        self.payload = {
            'minimumFirmwareVersion': min_version,
            'currentFirmwareVersion': cur_version
        }
        super(TargetFirmwareOutdatedError, self).__init__(*args, **kwargs)


class TargetBridgeFirmwareOutdatedError(AskhomeException):
    """Amazon docs: Indicates that the home automation hub or bridge that connects the target device
    has outdated firmware.
    """
    def __init__(self, min_version, cur_version, *args, **kwargs):
        self.payload = {
            'minimumFirmwareVersion': min_version,
            'currentFirmwareVersion': cur_version
        }
        super(TargetBridgeFirmwareOutdatedError, self).__init__(*args, **kwargs)


class TargetHardwareMalfunctionError(AskhomeException):
    """Amazon docs: Indicates that the target device experienced a hardware malfunction."""


class TargetBridgeHardwareMalfunctionError(AskhomeException):
    """Amazon docs: Indicates that the home automation hub or bridge connecting the target device
    experienced a hardware malfunction
    """


class UnableToGetValueError(AskhomeException):
    """Amazon docs: Indicates that an error occurred while trying to get the specified value on
    the target device. When returning this error, an appropriate error_code value enables
    Alexa to respond appropriately for different kinds of failures. You only need to generate an
    error code appropriate for the target device.
    """
    namespace = 'Alexa.ConnectedHome.Query'

    def __init__(self, error_code, error_description=None, *args, **kwargs):
        """
        Args:
            error_code (str): Possible error codes are:
                * DEVICE_AJAR: Cannot get the specified state because the door is open.
                * DEVICE_BUSY: The device is busy
                * DEVICE_JAMMED: The device is jammed.
                * DEVICE_OVERHEATED: The device has overheated.
                * HARDWARE_FAILURE: Request failed because of an undetermined hardware failure.
                * LOW_BATTERY: The device's battery is low
                * NOT_CALIBRATED: The device is not calibrated.
            error_description (str): non-required custom description
        """
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnableToGetValueError, self).__init__(*args, **kwargs)


class UnableToSetValueError(AskhomeException):
    """Amazon docs: Indicates that an error occurred while trying to set the specified value on
    the target device. When returning this error, an appropriate error_code value enables
    Alexa to respond appropriately for different kinds of failures. You only need to generate
    error codes appropriate for the target device.
    """
    def __init__(self, error_code, error_description=None, *args, **kwargs):
        """
        Args:
            error_code (str): Possible error codes are:
                * DEVICE_AJAR: Cannot get the specified state because the door is open.
                * DEVICE_BUSY: The device is busy
                * DEVICE_JAMMED: The device is jammed.
                * DEVICE_OVERHEATED: The device has overheated.
                * HARDWARE_FAILURE: Request failed because of an undetermined hardware failure.
                * LOW_BATTERY: The device's battery is low
                * NOT_CALIBRATED: The device is not calibrated.
            error_description (str): non-required custom description
        """
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnableToSetValueError, self).__init__(*args, **kwargs)


class UnwillingToSetValueError(AskhomeException):
    """Amazon docs: Indicates that the target device partner is unwilling to set the requested
    value on the specified device. Use this error for temperature settings.
    """
    def __init__(self, error_code='ThermostatIsOff', error_description=None, *args, **kwargs):
        self.payload = {'errorInfo': {'code': error_code}}
        if error_description is not None:
            self.payload['errorInfo']['description'] = error_description
        super(UnwillingToSetValueError, self).__init__(*args, **kwargs)


class RateLimitExceededError(AskhomeException):
    """Amazon docs: Indicates that the maximum number of requests that a device accepts has been
    exceeded. This message provides information about the maximum number of requests for a device
    and the time unit for those requests. For example, if a device accepts four requests per
    hour, the message should specify 4 and HOUR as rate_limit and time_unit, respectively.
    """
    def __init__(self, rate_limit, time_unit='HOUR', *args, **kwargs):
        self.payload = {
            'rateLimit': rate_limit,
            'timeUnit': time_unit
        }
        super(RateLimitExceededError, self).__init__(*args, **kwargs)


class NotSupportedInCurrentModeError(AskhomeException):
    """Amazon docs: Indicates that the target device is in a mode in which it cannot be
    controlled with the Smart Home Skill API, and provides information about the current mode of
    the device.
    """
    def __init__(self, current_mode, *args, **kwargs):
        self.payload = {'currentDeviceMode': current_mode}
        super(NotSupportedInCurrentModeError, self).__init__(*args, **kwargs)


# Other Faults

class ExpiredAccessTokenError(AskhomeException):
    """Amazon docs: Indicates that the access token used for authentication has expired and is no
    longer valid.
    """


class InvalidAccessTokenError(AskhomeException):
    """Amazon docs: Indicates that the access token used for authentication is not valid for
    a reason other than it has expired.
    """


class UnsupportedTargetError(AskhomeException):
    """Amazon docs: Indicates that the target device is not supported by the skill adapter."""


class UnsupportedOperationError(AskhomeException):
    """Amazon docs: Indicates that the requested operation is not supported on the target device."""


class UnsupportedTargetSettingError(AskhomeException):
    """Amazon docs: Indicates that the requested setting is not valid for the specified device and
    operation.
    """


class UnexpectedInformationReceivedError(AskhomeException):
    """Amazon docs: The request message or payload could not be handled by the skill adapter because
    it was malformed.
    """
    def __init__(self, faulting_parameter, *args, **kwargs):
        self.payload = {'faultingParameter': faulting_parameter}
        super(UnexpectedInformationReceivedError, self).__init__(*args, **kwargs)
