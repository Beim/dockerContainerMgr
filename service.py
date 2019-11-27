import docker
from typing import List, Dict
from docker.models.containers import Container
import psutil

from config.config import CONFIG


class DockerService:

    def __init__(self, client: docker.DockerClient):
        self.client = client

    def get_container_ids(self, show_all: bool = False) -> List[str]:
        """
        获取容器id list
        :return: 容器id list
        """
        filters = {
            "ancestor": CONFIG["image"],
            "label": CONFIG["labels"]
        }
        containers = self.client.containers.list(all=show_all, filters=filters)
        result = []
        for container in containers:
            result.append(container.attrs['Config']['Hostname'])
        return result

    def _get_containers(self, show_all: bool = False) -> List[Container]:
        """
        获取容器 list
        :return: 容器 list
        """
        filters = {
            "ancestor": CONFIG["image"],
            "label": CONFIG["labels"]
        }
        return self.client.containers.list(all=show_all, filters=filters)

    def run_container(self) -> Dict:
        """
        run容器
        :return: 容器id 与端口号，若超过容器数量限制，返回None
        """
        if psutil.virtual_memory().percent >= CONFIG['max_memory_usage']:
            return None
        container = self.client.containers.run(CONFIG["image"], detach=True,
                                         environment=CONFIG["environment"],
                                         ports=CONFIG["ports"],
                                         labels=CONFIG['labels'])
        return DockerService._parse_container_attrs(container)

    def stop_container_by_id(self, container_id: str) -> None:
        """
        stop 容器
        :param container_id:
        :return: None
        """
        container = self.client.containers.get(container_id)
        container.stop()

    def start_container_by_id(self, container_id: str) -> None:
        """
        start 容器
        :param container_id:
        :return:
        """
        container = self.client.containers.get(container_id)
        container.start()

    def get_container_status(self, container_id: str):
        """
        获取指定Id 容器运行状态&暴露的端口
        :param container_id:
        :return:
        """
        container = self.client.containers.get(container_id)
        return DockerService._parse_container_attrs(container)

    @staticmethod
    def _parse_container_attrs(container: Container) -> dict:
        """
        解析容器属性
        :param container:
        :return:
        """
        result = {
            "id": container.short_id,
            "status": container.status,
            "ports": None
        }
        if container.status == "running":
            result['ports'] = {
                '7474': container.ports['7474/tcp'][0]['HostPort'],
                '7687': container.ports['7687/tcp'][0]['HostPort']
            }
        return result

    def stop_all_containers(self) -> None:
        """
        停止所有容器
        :return:
        """
        containers = self._get_containers(show_all=False)
        for container in containers:
            if container.status == 'running':
                container.stop()

    def remove_all_containers(self) -> None:
        """
        移除所有未运行的容器
        :return:
        """
        containers = self._get_containers(show_all=True)
        for container in containers:
            if container.status != 'running':
                container.remove()


if __name__ == '__main__':
    docker_client = docker.from_env()
    service = DockerService(docker_client)
    service.stop_all_containers()
    service.remove_all_containers()
    # print(service.run_container())
    # print(service.get_container_status("ca4ce4c4cfe4"))
