from smarthome import Smarthome, Device
import pytest


@pytest.fixture
def discover_request():
    return {
        "header": {
            "messageId": "6d6d6e14-8aee-473e-8c24-0d31ff9c17a2",
            "name": "DiscoverAppliancesRequest",
            "namespace": "Alexa.ConnectedHome.Discovery",
            "payloadVersion": "2"
        },
        "payload": {
            "accessToken": "OAuth Token"
        }
    }


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


def test_smarthome_handle_discover(discover_request, discover_response):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            return 1

    home = Smarthome()
    home.add_device('123', Light, friendly_name="Kitchen Light")

    response = home.handle(discover_request)

    assert response == discover_response


def test_smarthome_discover_decorator(discover_request, discover_response):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            return 1

    home = Smarthome()

    @home.handle_discovery
    def discover(request):
        home.add_device('123', Light, friendly_name="Kitchen Light")
        return home.discover(request)

    response = home.handle(discover_request)

    assert response == discover_response


def test_smarthome_discover_device_details(discover_request):
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            return 1

        class Details:
            manufacturer = "EvilCorp"

    home = Smarthome()
    home.add_device('123', Light, friendly_name="Kitchen Light")
    home.add_device('456', Light, friendly_name="Bedroom Light", manufacturer="GoodCorp")

    response = home.handle(discover_request)

    assert response["payload"]["discoveredAppliances"][0]["manufacturerName"] == "EvilCorp"
    assert response["payload"]["discoveredAppliances"][1]["manufacturerName"] == "GoodCorp"

