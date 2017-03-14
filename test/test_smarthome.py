import pytest

from smarthome import Smarthome, Appliance
from smarthome.exceptions import TargetOfflineError


@pytest.fixture
def discover_response():
    return {
        'header': {
            'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2',
            'name': 'DiscoverAppliancesResponse',
            'namespace': 'Alexa.ConnectedHome.Discovery',
            'payloadVersion': '2'
        },
        'payload': {
            'discoveredAppliances': [
                {
                    'actions': [
                        'turnOn'
                    ],
                    'additionalApplianceDetails': {},
                    'applianceId': '123',
                    'friendlyName': 'Kitchen Light',
                    'friendlyDescription': '',
                    'isReachable': True,
                    'manufacturerName': '',
                    'modelName': '',
                    'version': ''
                }
            ]
        }
    }


def test_handle_discover(discover_request, discover_response):
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

    home = Smarthome()
    home.add_appliance('123', Light, name='Kitchen Light')

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_discover_decorator(discover_request, discover_response):
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

    home = Smarthome()

    @home.discover
    def discover(request):
        home.add_appliance('123', Light, name='Kitchen Light')
        return request.response(home)

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_get_device_decorator():
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            return request.response(payload={'foo': 'bar'})

    home = Smarthome()

    @home.get_appliance
    def get_appliance(request):
        return Light

    request = {
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light1'
            }
        }
    }
    response = home.lambda_handler(request)

    assert response == {
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnConfirmation',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {'foo': 'bar'}
    }


def test_discover_appliance_details(discover_request):
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

        class Details:
            manufacturer = 'EvilCorp'

    class Door(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

    home = Smarthome(manufacturer='NeutralCorp')
    home.add_appliance('1', Light, name='Kitchen Light')
    home.add_appliance('2', Light, name='Bedroom Light', manufacturer='GoodCorp')
    home.add_appliance('3', Door, name='Front Door', manufacturer='NeutralCorp')

    response = home.lambda_handler(discover_request)

    appls = {appl['applianceId']: appl['manufacturerName']
             for appl in response['payload']['discoveredAppliances']}
    assert appls['1'] == 'EvilCorp'
    assert appls['2'] == 'GoodCorp'
    assert appls['3'] == 'NeutralCorp'


def test_appliance_not_found():
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

    home = Smarthome()
    home.add_appliance('light1', Light)

    response = home.lambda_handler({
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light2'
            }
        }
    })
    assert response == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'UnsupportedTargetError',
            'payloadVersion': '2',
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688'
        },
        'payload': {}
    }

    response = home.lambda_handler({
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOffRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light1'
            }
        }
    })
    assert response == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'UnsupportedOperationError',
            'payloadVersion': '2',
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688'
        },
        'payload': {}
    }


def test_full_usage(discover_request):
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            pass

        @Appliance.action
        def set_target_temperature(self, request):
            raise TargetOfflineError

        @Appliance.query
        def get_target_temperature(self, request):
            return request.response(27.6)

    home = Smarthome()
    home.add_appliance('light1', Light, name='Kitchen Light')

    response = home.lambda_handler(discover_request)
    assert response == {
        'header': {
            'messageId': '6d6d6e14-8aee-473e-8c24-0d31ff9c17a2',
            'name': 'DiscoverAppliancesResponse',
            'namespace': 'Alexa.ConnectedHome.Discovery',
            'payloadVersion': '2'
        },
        'payload': {
            'discoveredAppliances': [
                {
                    'actions': [
                        'setTargetTemperature',
                        'turnOn'
                    ],
                    'additionalApplianceDetails': {},
                    'applianceId': 'light1',
                    'friendlyName': 'Kitchen Light',
                    'friendlyDescription': '',
                    'isReachable': True,
                    'manufacturerName': '',
                    'modelName': '',
                    'version': ''
                }
            ]
        }
    }

    response = home.lambda_handler({
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light1'
            }
        }
    })
    assert response == {
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnConfirmation',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {}
    }

    response = home.lambda_handler({
        'header': {
            'messageId': 'b6602211-b4b3-4960-b063-f7e3967c00c4',
            'name': 'SetTargetTemperatureRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light1'
            },
            'targetTemperature': {
                'value': 25.0
            }
        }
    })
    assert response == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Control',
            'name': 'TargetOfflineError',
            'payloadVersion': '2',
            'messageId': 'b6602211-b4b3-4960-b063-f7e3967c00c4'
        },
        'payload': {}
    }

    response = home.lambda_handler({
        'header': {
            'messageId': 'b6602211-b4b3-4960-b063-f7e3967c00c4',
            'name': 'GetTargetTemperatureRequest',
            'namespace': 'Alexa.ConnectedHome.Query',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {},
                'applianceId': 'light1'
            }
        }
    })
    assert response == {
        'header': {
            'namespace': 'Alexa.ConnectedHome.Query',
            'name': 'GetTargetTemperatureResponse',
            'payloadVersion': '2',
            'messageId': 'b6602211-b4b3-4960-b063-f7e3967c00c4'
        },
        'payload': {
            'targetTemperature': {
                'value': 27.6
            },
            'temperatureMode': {
                'value': 'AUTO'
            }
        }
    }
