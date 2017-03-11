from smarthome import Request


def test_discovery_creation(discover_request):
    request = Request(discover_request)
    assert request.data == discover_request
    assert request.name == "DiscoverAppliancesRequest"
