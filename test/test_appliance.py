from smarthome import Appliance, Request


def test_action_definition():
    class Light(Appliance):
        @Appliance.action
        def turn_on(self, request):
            return 1

    class Door(Appliance):
        @Appliance.action
        def turn_on(self, request):
            return 2

    l = Light()
    # Test that the actions are independent in each class
    assert l.actions['turnOn'](l, None) == 1
    assert Light.actions == {'turnOn': Light.turn_on.__func__}
    assert Light.request_handlers == {'TurnOnRequest': Light.turn_on.__func__}


def test_action_for_definition():
    class Light(Appliance):
        @Appliance.action_for('turnOn', 'TurnOffRequest', 'set_percentage')
        def control(self, request):
            return 1

    assert Light.actions == {
        'turnOn': Light.control.__func__,
        'turnOff': Light.control.__func__,
        'setPercentage': Light.control.__func__,
    }
    assert Light.request_handlers == {
        'TurnOnRequest': Light.control.__func__,
        'TurnOffRequest': Light.control.__func__,
        'SetPercentageRequest': Light.control.__func__,
    }


def test_query_definition():
    class Light(Appliance):
        @Appliance.query
        def get_target_temperature(self, request):
            return 42

    l = Light()
    assert len(l.actions) == 0
    assert Light.request_handlers == {'GetTargetTemperatureRequest': Light.get_target_temperature.__func__}


def test_init():
    request = Request({
        'header': {
            'messageId': '01ebf625-0b89-4c4d-b3aa-32340e894688',
            'name': 'TurnOnRequest',
            'namespace': 'Alexa.ConnectedHome.Control',
            'payloadVersion': '2'
        },
        'payload': {
            'accessToken': '[OAuth token here]',
            'appliance': {
                'additionalApplianceDetails': {'foo': 'bar'},
                'applianceId': 'light1'
            }
        }
    })
    appliance = Appliance(request)

    assert appliance.id == 'light1'
    assert appliance.additional_details == {'foo': 'bar'}
