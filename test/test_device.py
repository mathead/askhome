from smarthome import Device

def test_device_action_definition():
    class Light(Device):
        @Device.action
        def turnOn(self, request):
            return 1

    class Door(Device):
        @Device.action
        def turnOn(self, request):
            return 2

    l = Light()
    assert l.actions["turnOn"](l, None) == 1
    assert Light.actions == {"turnOn": Light.turnOn.__func__}


