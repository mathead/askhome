from smarthome import Device


def test_action_definition():
    class Light(Device):
        @Device.action
        def turn_on(self, request):
            return 1

    class Door(Device):
        @Device.action
        def turn_on(self, request):
            return 2

    l = Light()
    # Test that the actions are independent in each class
    assert l.actions["turnOn"](l, None) == 1
    assert Light.actions == {"turnOn": Light.turn_on.__func__}
    assert Light.request_handlers == {"TurnOnRequest": Light.turn_on.__func__}


def test_action_for_definition():
    class Light(Device):
        @Device.action_for("turnOn", "TurnOffRequest", "set_percentage")
        def control(self, request):
            return 1

    assert Light.actions == {
        "turnOn": Light.control.__func__,
        "turnOff": Light.control.__func__,
        "setPercentage": Light.control.__func__,
    }
    assert Light.request_handlers == {
        "TurnOnRequest": Light.control.__func__,
        "TurnOffRequest": Light.control.__func__,
        "SetPercentageRequest": Light.control.__func__,
    }


def test_query_definition():
    class Light(Device):
        @Device.query
        def get_target_temperature(self, request):
            return 42

    l = Light()
    assert len(l.actions) == 0
    assert Light.request_handlers == {"GetTargetTemperatureRequest": Light.get_target_temperature.__func__}
