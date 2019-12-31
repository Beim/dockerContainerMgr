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

    def run_container(self, http_port: str = None, bolt_port: str = None) -> Dict:
        """
        run 容器
        :param http_port: 映射到主机的http 端口
        :param bolt_port: 映射到主机的bolt 端口
        :return: 容器id 与端口号，若超过容器数量限制报错
        """
        if psutil.virtual_memory().percent >= CONFIG['max_memory_usage']:
            raise RuntimeError("exceed max_memory_usage: %s" % psutil.virtual_memory().percent)
        container = self.client.containers.run(CONFIG["image"], detach=True,
                                         environment=CONFIG["environment"],
                                         ports={ '7474/tcp': bolt_port, '7687/tcp': http_port },
                                         labels=CONFIG['labels'])
        return DockerService._parse_container_attrs(container)

    def run_container_with_port_constraint(self) -> Dict:
        """
        启动容器，暴露的端口在配置的端口区间内
        :return:
        """
        ports_range_set = set()
        for r in CONFIG['ports']:
            [start, end] = r.split("-")
            start = int(start)
            end = int(end)
            for p in range(start, end + 1):
                ports_range_set.add(str(p))

        used_ports = set()
        filters = {
            "ancestor": CONFIG["image"],
            # "label": CONFIG["labels"]
        }
        containers = self.client.containers.list(all=False, filters=filters)
        for c in containers:
            used_ports.add(c.ports['7474/tcp'][0]['HostPort'])
            used_ports.add(c.ports['7687/tcp'][0]['HostPort'])

        available_ports = list(ports_range_set - used_ports)
        available_ports.sort()
        if len(available_ports) < 2:
            raise RuntimeError("no ports available")
        return self.run_container(http_port=available_ports[0], bolt_port=available_ports[1])

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
    print(service.run_container_with_port_constraint())
    # service.stop_all_containers()
    # service.remove_all_containers()
    # print(service.run_container())
    # print(service.get_container_status("ca4ce4c4cfe4"))
