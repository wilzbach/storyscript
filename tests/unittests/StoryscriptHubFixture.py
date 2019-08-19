import sys
from os import path


sys.path.insert(
    0, path.dirname(path.dirname(path.dirname(path.realpath(__file__)))))

from tests.e2e.helpers.StoryscriptHubFixture import ServiceWrapper, \
    StoryscriptHubFixture   # noqa: E402


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
