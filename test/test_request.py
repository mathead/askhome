from smarthome import Request


def test_discovery_request(discover_request):
    request = Request(discover_request)
    assert request.data == discover_request
    assert request.name == "DiscoverAppliancesRequest"


def test_set_temperature_request():
    request = Request({
        "header": {
            "namespace": "Alexa.ConnectedHome.Control",
            "name": "SetTargetTemperatureRequest",
            "payloadVersion": "2",
            "messageId": "23624201-23a5-44c3-8fdc-ec6c4b6c3df8"
        },
        "payload": {
            "accessToken": "[OAuth token here]",
            "appliance": {
                "applianceId": "[Device ID for Bedroom Thermostat]"
            },
            "targetTemperature": {
                "value": 27.6
            }
        }
    })

    assert request.temperature.target == 27.6
    assert request.temperature.delta is None

def test_increment_temperature_response():
    request = Request({
        "header": {
            "namespace": "Alexa.ConnectedHome.Control",
            "name": "IncrementTemperatureRequest",
            "payloadVersion": "2",
            "messageId": "23624201-23a5-44c3-8fdc-ec6c4b6c3df8"
        },
        "payload": {
            "accessToken": "[OAuth token here]",
            "appliance": {
                "applianceId": "[Device ID for Bedroom Thermostat]"
            },
            "deltaTemperature": {
                "value": 1
            }
        }
    })

    assert request.response_header() == {
        "namespace": "Alexa.ConnectedHome.Control",
        "name": "SetTargetTemperatureConfirmation",
        "payloadVersion": "2",
        "messageId": "23624201-23a5-44c3-8fdc-ec6c4b6c3df8"
    }

    assert request.response(temperature=28.6, mode="HEAT", previous_temperature=27.6) == {
        "header": {
            "messageId": "780013dd-99d0-4c69-9e35-db0457f9f2a7",
            "name": "IncrementTargetTemperatureConfirmation",
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        "payload": {
            "previousState": {
                "mode": {
                    "value": "AUTO"
                },
                "targetTemperature": {
                    "value": 27.6
                }
            },
            "targetTemperature": {
                "value": 28.6
            },
            "temperatureMode": {
                "value": "HEAT"
            }
        }
    }
