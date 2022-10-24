from testcontainers.elasticsearch import (
    ElasticSearchContainer,
    DockerContainer,
    _major_version_from_image_name,
    _environment_by_version,
)
from testcontainers.core.waiting_utils import wait_container_is_ready
import urllib


class CustomElasticSearchContainer(ElasticSearchContainer):
    """
    Custom ElasticSearch container.

    Example
    -------
    ::

        with ElasticSearchContainer() as es:
            connection_url = es.get_url()
    """

    def __init__(self, image="elasticsearch", port_to_expose=9200, **kwargs):
        super(ElasticSearchContainer, self).__init__(image, **kwargs)
        self.port_to_expose = port_to_expose
        self.with_exposed_ports(self.port_to_expose)
        self.with_env("transport.host", "127.0.0.1")
        self.with_env("http.host", "0.0.0.0")

        major_version = _major_version_from_image_name(image)
        for key, value in _environment_by_version(major_version).items():
            self.with_env(key, value)

    @wait_container_is_ready()
    def _connect(self):
        res = urllib.request.urlopen(self.get_url())
        if res.status != 200:
            raise Exception()

    def get_url(self):
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port_to_expose)
        return "http://{}:{}".format(host, port)

    def start(self):
        super().start()
        self._connect()
        return self

    def with_exposed_ports(self, *ports) -> "DockerContainer":
        for port in list(ports):
            self.ports[port] = port
        return self

    # TODO: Method for checking if a connection already exists

    # TODO: Method to stop and remove container
