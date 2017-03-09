from smarthome import Smarthome, Device

def test_smarthome_handle_discover():
    class Light(Device):
        @Device.action
        def turnOn(self, request):
            return 1

    home = Smarthome()
    home.add_device('123', Light, friendly_name="Kitchen Light")

    request = {
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
    response = home.handle(request)

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

def test_smarthome_discover_decorator():
    class Light(Device):
        @Device.action
        def turnOn(self, request):
            return 1

    home = Smarthome()

    @home.handle_discovery
    def discover(request):
        home.add_device('123', Light, friendly_name="Kitchen Light")
        return home.discover(request)

    request = {
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
    response = home.handle(request)

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

