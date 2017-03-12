import pytest

from smarthome import Smarthome, Device
from smarthome.exceptions import TargetOfflineError


@pytest.fixture
def discover_response():
    return {
        "header": {
            "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
            "name": "DiscoverAppliancesResponse",
            "namespace": "Alexa.ConnectedHome.Discovery",
            "payloadVersion": "2"
        },
        "payload": {
            "discoveredAppliances": [
                {
                    "actions": [
                        "turnOn"
                    ],
                    "additionalApplianceDetails": {},
                    "applianceId": "123",
                    "friendlyName": "Kitchen Light",
                    "friendlyDescription": "",
                    "isReachable": True,
                    "manufacturerName": "",
                    "modelName": "",
                    "version": ""
                }
            ]
        }
    }


def test_handle_discover(discover_request, discover_response):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            pass

    home = Smarthome()
    home.add_device('123', Light, friendly_name="Kitchen Light")

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_discover_decorator(discover_request, discover_response):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            pass

    home = Smarthome()

    @home.discover
    def discover(request):
        home.add_device('123', Light, friendly_name="Kitchen Light")
        return request.response(home)

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_get_device_decorator():
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            return {"foo": "bar"}

    home = Smarthome()

    @home.get_device
    def get_device(request):
        return Light

    request = {
        "header": {
            "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
            "name": "TurnOnRequest",
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        "payload": {
            "accessToken": "[OAuth token here]",
            "appliance": {
                "additionalApplianceDetails": {},
                "applianceId": "light1"
            }
        }
    }
    response = home.lambda_handler(request)

    assert response == {
        "header": {
            "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
            "name": "TurnOnConfirmation",
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        "payload": {"foo": "bar"}
    }


def test_discover_device_details(discover_request):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            pass

        class Details:
            manufacturer = "EvilCorp"

    home = Smarthome()
    home.add_device('123', Light, friendly_name="Kitchen Light")
    home.add_device('456', Light, friendly_name="Bedroom Light", manufacturer="GoodCorp")

    response = home.lambda_handler(discover_request)

    assert response["payload"]["discoveredAppliances"][0]["manufacturerName"] == "EvilCorp"
    assert response["payload"]["discoveredAppliances"][1]["manufacturerName"] == "GoodCorp"


def test_full_usage(discover_request):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            pass

        @Device.action
        def set_target_temperature(self, request):
            raise TargetOfflineError

        @Device.query
        def get_target_temperature(self, request):
            return request.response(27.6)

    home = Smarthome()
    home.add_device('light1', Light, friendly_name="Kitchen Light")

    response = home.lambda_handler(discover_request)
    assert response == {
        "header": {
            "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
            "name": "DiscoverAppliancesResponse",
            "namespace": "Alexa.ConnectedHome.Discovery",
            "payloadVersion": "2"
        },
        "payload": {
            "discoveredAppliances": [
                {
                    "actions": [
                        "turnOn",
                        "setTemperature"
                    ],
                    "additionalApplianceDetails": {},
                    "applianceId": "light1",
                    "friendlyName": "Kitchen Light",
                    "friendlyDescription": "",
                    "isReachable": True,
                    "manufacturerName": "",
                    "modelName": "",
                    "version": ""
                }
            ]
        }
    }

    response = home.lambda_handler({
        "header": {
            "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
            "name": "TurnOnRequest",
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        "payload": {
            "accessToken": "[OAuth token here]",
            "appliance": {
                "additionalApplianceDetails": {},
                "applianceId": "light1"
            }
        }
    })
    assert response == {
        {
            "header": {
                "messageId": "01ebf625-0b89-4c4d-b3aa-32340e894688",
                "name": "TurnOnConfirmation",
                "namespace": "Alexa.ConnectedHome.Control",
                "payloadVersion": "2"
            },
            "payload": {}
        }
    }

    response = home.lambda_handler({
        "header": {
            "messageId": "b6602211-b4b3-4960-b063-f7e3967c00c4",
            "name": "SetTargetTemperatureRequest",
            "namespace": "Alexa.ConnectedHome.Control",
            "payloadVersion": "2"
        },
        "payload": {
            "accessToken": "[OAuth token here]",
            "appliance": {
                "additionalApplianceDetails": {},
                "applianceId": "light1"
            },
            "targetTemperature": {
                "value": 25.0
            }
        }
    })
    assert response == {
        "header": {
            "namespace": "Alexa.ConnectedHome.Control",
            "name": "TargetOfflineError",
            "payloadVersion": "2",
            "messageId": "b6602211-b4b3-4960-b063-f7e3967c00c4"
        },
        "payload": {}
    }


