import pytest

from askhome import Appliance


@pytest.fixture(scope='module')
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


@pytest.fixture(scope='module')
def Light():
    class Light2(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

    return Light2
