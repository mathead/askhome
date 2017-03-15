from datetime import datetime

from askhome import Request


def test_discovery_request(discover_request):
    request = Request(discover_request, {'context': 'object'})
    assert request.data == discover_request
    assert request.header == discover_request['header']
    assert request.payload == discover_request['payload']
    assert request.context == {'context': 'object'}
    assert request.name == 'DiscoverAppliancesRequest'
    assert request.access_token == "OAuth Token"
    assert request.appliance_id is None
    assert request.appliance_details is None


def test_set_temperature_request():
    request = Request({
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'SetTargetTemperatureRequest',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'applianceId': 'thermostat1',
                'additionalApplianceDetails': {'foo': 'bar'}
            },
            'targetTemperature': {
                'value': 27.6
            }
        }
    })

    assert request.appliance_id == 'thermostat1'
    assert request.appliance_details == {'foo': 'bar'}
    assert request.temperature == 27.6
    assert request.delta_temperature is None


def test_increment_temperature_response():
    request = Request({
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'IncrementTargetTemperatureRequest',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'applianceId': '[Device ID for Bedroom Thermostat]'
            },
            'deltaTemperature': {
                'value': 1
            }
        }
    })

    assert request.temperature is None
    assert request.delta_temperature == 1

    assert request.response_header() == {
        'namespace': 'Alexa.ConnectedHome.Control',
        'name': 'IncrementTargetTemperatureConfirmation',
        'payloadVersion': '2',
        'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
    }

    assert request.response(temperature=28.6, mode='HEAT', previous_temperature=27.6) == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'IncrementTargetTemperatureConfirmation',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'previousState': {
                'mode': {
                    'value': 'AUTO'
                },
                'targetTemperature': {
                    'value': 27.6
                }
            },
            'targetTemperature': {
                'value': 28.6
            },
            'temperatureMode': {
                'value': 'HEAT'
            }
        }
    }


def test_get_temperature_response():
    request = Request({
        'header': {
            'namespace': 'Alexa.ConnectedHome.Query',
            'name': 'GetTargetTemperatureRequest',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'applianceId': '[Device ID for Bedroom Thermostat]'
            }
        }
    })

    assert request.response(cooling_temperature=23.89, heating_temperature=22.20, mode='CUSTOM',
                            mode_name='Custom mode', timestamp=datetime(2017, 3, 14, 23, 20, 50)) == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Query',
            'name': 'GetTargetTemperatureResponse',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'coolingTargetTemperature': {
                'value': 23.89,
            },
            'heatingTargetTemperature': {
                'value': 22.20,
            },
            'applianceResponseTimestamp': '2017-03-14T23:20:50',
            'temperatureMode': {
                'value': 'CUSTOM',
                'friendlyName': 'Custom mode'
            }
        }
    }


def test_temperature_reading_response():
    request = Request({
        'header': {
            'namespace': 'Alexa.ConnectedHome.Query',
            'name': 'GetTemperatureReadingRequest',
            'payloadVersion': '2',
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'applianceId': '[Device ID for Bedroom Thermostat]'
            }
        }
    })

    assert request.response(21.11, timestamp='2017-01-12T23:20:50.52Z') == {
        'header': {
            'messageId': '23624201-23a5-44c3-8fdc-ec6c4b6c3df8',
            'name': 'GetTemperatureReadingResponse',
            'namespace': 'Alexa.ConnectedHome.Query',
            'payloadVersion': '2'
        },
        'payload': {
            'temperatureReading': {
                'value': 21.11
            },
            'applianceResponseTimestamp': '2017-01-12T23:20:50.52Z'
        }
    }


def test_increment_percentage():
    request = Request({
        'header': {
            'messageId': '95872301-4ff6-4146-b3a4-ae84c760c13e',
            'name': 'IncrementPercentageRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': '[Device ID for Cinema Room Light]'
            },
            'deltaPercentage': {
                'value': 5.0
            }
        }
    })

    assert request.percentage is None
    assert request.delta_percentage == 5.0


def test_set_percentage_custom_payload_response():
    request = Request({
        'header': {
            'messageId': '95872301-4ff6-4146-b3a4-ae84c760c13e',
            'name': 'SetPercentageRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': '[Device ID for Cinema Room Light]'
            },
            'percentageState': {
                'value': 50.0
            }
        }
    })

    assert request.percentage == 50.0
    assert request.delta_percentage is None

    assert request.response(payload={'foo': 'bar'}) == {
        'header': {
            'messageId': '95872301-4ff6-4146-b3a4-ae84c760c13e',
            'name': 'SetPercentageConfirmation',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {'foo': 'bar'}
    }


def test_set_lock_state():
    request = Request({
        'header': {
            'messageId': '95872301-4ff6-4146-b3a4-ae84c760c13e',
            'name': 'SetLockStateRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': '[Device ID for front door lock appliance]'
            },
            'lockState': 'LOCKED'
        }
    })

    assert request.lock_state == 'LOCKED'

    assert request.response('UNLOCKED') == {
        'header': {
            'messageId': '95872301-4ff6-4146-b3a4-ae84c760c13e',
            'name': 'SetLockStateConfirmation',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'lockState': 'UNLOCKED'
        }
    }


def test_health_check():
    request = Request({
        'header': {
            'messageId': '243550dc-5f95-4ae4-ad43-4e1e7cb037fd',
            'name': 'HealthCheckRequest',
            'namespace': 'Alexa.ConnectedHome.System',
            'payloadVersion': '2'
        },
        'payload': {
            'initiationTimestamp': '1435302567000'
        }
    })

    # Just for that sweet 100% test coverage
    assert request.lock_state is None

    assert request.response(False, 'The system is currently not healthy') == {
        'header': {
            'messageId': '243550dc-5f95-4ae4-ad43-4e1e7cb037fd',
            'name': 'HealthCheckResponse',
            'namespace': 'Alexa.ConnectedHome.System',
            'payloadVersion': '2'
        },
        'payload': {
            'isHealthy': False,
            'description': 'The system is currently not healthy'
        }
    }