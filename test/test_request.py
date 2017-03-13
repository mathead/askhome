from smarthome import Request


def test_discovery_request(discover_request):
    request = Request(discover_request, {'context': 'object'})
    assert request.data == discover_request
    assert request.header == discover_request['header']
    assert request.payload == discover_request['payload']
    assert request.context == {'context': 'object'}
    assert request.name == 'DiscoverAppliancesRequest'
    assert request.access_token == "OAuth Token"


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
