import pytest

from askhome import Smarthome, Appliance
from askhome.exceptions import TargetOfflineError


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
                    'friendlyDescription': 'No description',
                    'isReachable': True,
                    'manufacturerName': 'Unknown manufacturer',
                    'modelName': 'Unknown model',
                    'version': 'v1'
                }
            ]
        }
    }


def test_handle_discover(discover_request, discover_response, Light):
    home = Smarthome()
    home.add_appliance('123', Light, name='Kitchen Light')

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_discover_decorator(discover_request, discover_response, Light):
    home = Smarthome()

    @home.discover_handler
    def discover(request):
        home.add_appliance('123', Light, name='Kitchen Light')
        return request.response(home)

    response = home.lambda_handler(discover_request)

    assert response == discover_response


def test_get_device_decorator():
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            return request.raw_response({'foo': self.id})

    home = Smarthome()

    @home.get_appliance_handler
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
        'payload': {'foo': 'light1'}
    }


def test_discover_appliance_details(discover_request, Light):
    class Door(Appliance):
        @Appliance.action
        def turn_on(self, request):
            return 1

        class Details:
            manufacturer = 'EvilCorp'

    home = Smarthome(manufacturer='NeutralCorp')
    home.add_appliance('1', Door, name='Front Door')
    home.add_appliance('2', Door, name='Back Door', manufacturer='GoodCorp')
    home.add_appliance('3', Light, name='Kitchen Light', manufacturer='NeutralCorp')

    response = home.lambda_handler(discover_request)

    appls = {appl['applianceId']: appl['manufacturerName']
             for appl in response['payload']['discoveredAppliances']}
    assert appls['1'] == 'EvilCorp'
    assert appls['2'] == 'GoodCorp'
    assert appls['3'] == 'NeutralCorp'

    # Just for that coverage
    assert Door.actions['turnOn'](None, None) == 1


def test_action_return_none(Light):
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


def test_appliance_not_found(Light):
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

        @Appliance.action
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
                        'getTargetTemperature',
                        'setTargetTemperature',
                        'turnOn'
                    ],
                    'additionalApplianceDetails': {},
                    'applianceId': 'light1',
                    'friendlyName': 'Kitchen Light',
                    'friendlyDescription': 'No description',
                    'isReachable': True,
                    'manufacturerName': 'Unknown manufacturer',
                    'modelName': 'Unknown model',
                    'version': 'v1'
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
