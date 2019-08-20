from os import path

from storyhub.sdk.ServiceWrapper import ServiceWrapper


tests_dir = path.dirname(path.dirname(path.dirname(path.realpath(__file__))))
hub_fixtures_file = path.join(tests_dir,
                              'fixtures', 'hub_fixture.json.fixed')


class StoryscriptHubFixture:
    """
    Exposes various class functions for emitting and loading fixture data
    for the storyscript hub.
    """
    _fixed_service_wrapper = None

    def __init__(self):
        self.load_services_from_file()

    @classmethod
    def load_services_from_file(cls):
        """
        Loads services from files into the _fixed_service_wrapper
        each time it is called.
        """
        cls._fixed_service_wrapper = ServiceWrapper.from_json_file(
            hub_fixtures_file)

    @classmethod
    def update_hub_fixtures(cls, services):
        cls._fixed_service_wrapper = ServiceWrapper(services)
        cls._fixed_service_wrapper.as_json_file(hub_fixtures_file)

    def get(self, *args, **kwargs):
        return self._fixed_service_wrapper.get(args[0])
