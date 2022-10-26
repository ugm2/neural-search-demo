from contextlib import suppress
from testcontainers.elasticsearch import (
    ElasticSearchContainer,
    DockerContainer,
)
from testcontainers.core.docker_client import DockerClient
from testcontainers.core.utils import setup_logger
from testcontainers.core.waiting_utils import wait_container_is_ready

logger = setup_logger(__name__)


class CustomElasticSearchContainer(ElasticSearchContainer):
    """
    Custom ElasticSearch container.
    """

    def __init__(
        self,
        image="docker.elastic.co/elasticsearch/elasticsearch:7.9.2",
        port_to_expose=9200,
        name="elasticsearch",
        **kwargs
    ):
        super(CustomElasticSearchContainer, self).__init__(
            image, port_to_expose, **kwargs
        )
        self._name = name
        self._kwargs = kwargs

    def _container_already_running(self):
        container = self.get_wrapped_container()
        return container is not None and container.status == "created"

    @wait_container_is_ready()
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

    def _get_container_by_name(self, docker_client: DockerClient, name: str):
        with suppress(Exception):
            return docker_client.client.containers.get(name)
        return None

    # Overwritting DockerContainer.start()
    def start(self):
        logger.info("Pulling image %s", self.image)
        docker_client = self.get_docker_client()
        self._container = self._get_container_by_name(docker_client, self._name)
        if self._container is None:
            self._container = docker_client.run(
                self.image,
                command=self._command,
                detach=True,
                environment=self.env,
                ports=self.ports,
                name=self._name,
                volumes=self.volumes,
                **self._kwargs
            )
        else:
            self._container.restart()
        logger.info("Container started: %s", self._container.short_id)
        return self

    # TODO: Method to stop and remove container when deleted (garbage collector)

    # TODO: Don't create multiple ES instances with different names
