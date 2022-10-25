from testcontainers.elasticsearch import (
    ElasticSearchContainer,
    DockerContainer,
)


class CustomElasticSearchContainer(ElasticSearchContainer):
    """
    Custom ElasticSearch container.
    """

    def __init__(self, image="elasticsearch", port_to_expose=9200, **kwargs):
        super(CustomElasticSearchContainer, self).__init__(
            image, port_to_expose, **kwargs
        )

    def _container_already_running(self):
        container = self.get_wrapped_container()
        return container is not None and container.status == "created"

    def start_if_not_running(self):
        if not self._container_already_running():
            self.start()

    def with_exposed_ports(self, *ports) -> "DockerContainer":
        for port in list(ports):
            self.ports[port] = port
        return self

    def is_it_running(self):
        container = self.get_wrapped_container()
        return container is not None and container.status == "created"

    # TODO: Method to stop and remove container when deleted (garbage collector)

    # TODO: Don't create multiple ES instances with different names
