from askhome import Request
from askhome.exceptions import *


def test_exceptions(discover_request):
    request = Request(discover_request)

    assert request.exception_response(
        SmartHomeException(name='CustomError', payload={'foo': 'bar'})) == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'CustomError',
            'payloadVersion': '2',
            'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {'foo': 'bar'}
    }

    assert request.exception_response(
        ValueOutOfRangeError(15.0, 30.0)) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'ValueOutOfRangeError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            'minimumValue': 15.0,
            'maximumValue': 30.0
        }
    }

    assert request.exception_response(
        DependentServiceUnavailableError('Service Name')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'DependentServiceUnavailableError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {'dependentServiceName': 'Service Name'}
    }

    assert request.exception_response(
        TargetFirmwareOutdatedError('17', '6')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'TargetFirmwareOutdatedError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            'minimumFirmwareVersion': '17',
            'currentFirmwareVersion': '6'
        }
    }

    assert request.exception_response(
        TargetBridgeFirmwareOutdatedError('17', '6')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'TargetBridgeFirmwareOutdatedError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            'minimumFirmwareVersion': '17',
            'currentFirmwareVersion': '6'
        }
    }

    assert request.exception_response(
        UnableToGetValueError('DEVICE_JAMMED', 'description')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Query',
           'name': 'UnableToGetValueError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            'errorInfo': {
                'code': 'DEVICE_JAMMED',
                'description': 'description'
            }
        }
    }

    assert request.exception_response(
        UnableToSetValueError('DEVICE_JAMMED', 'description')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'UnableToSetValueError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            'errorInfo': {
                'code': 'DEVICE_JAMMED',
                'description': 'description'
            }
        }
    }

    assert request.exception_response(
        UnwillingToSetValueError('ThermostatIsOff', 'description')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'UnwillingToSetValueError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
           'errorInfo': {
               'code': 'ThermostatIsOff',
               'description': 'description'
           }
        }
    }

    assert request.exception_response(
        RateLimitExceededError(10, 'HOUR')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'RateLimitExceededError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {
            "rateLimit": 10,
            "timeUnit": "HOUR"
        }
    }

    assert request.exception_response(
        NotSupportedInCurrentModeError('AWAY')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'NotSupportedInCurrentModeError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {'currentDeviceMode': 'AWAY'}
    }

    assert request.exception_response(
        UnexpectedInformationReceivedError('value')) == {
        'header': {
           'namespace': 'Alexa.ConnectedHome.Control',
           'name': 'UnexpectedInformationReceivedError',
           'payloadVersion': '2',
           'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2'
        },
        'payload': {'faultingParameter': 'value'}
    }







