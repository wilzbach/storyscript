from tests.test_helpers import ServiceWrapper, StoryscriptHubFixture


def test_update_hub_fixtures(patch):
    services = [
        'awesome',
        'gmaps',
        'http',
    ]
    patch.init(ServiceWrapper)
    patch.object(ServiceWrapper, 'as_json_file')
    StoryscriptHubFixture.update_hub_fixtures(services)
    ServiceWrapper.__init__.assert_called_with(services)
    ServiceWrapper.as_json_file.assert_called()
