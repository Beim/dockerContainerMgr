import grpc
from concurrent import futures
import time
import docker
from google.protobuf import wrappers_pb2 as wrappers
from google.protobuf.empty_pb2 import Empty

from proto import dockerContainerMgr_pb2 as dcm, dockerContainerMgr_pb2_grpc as dcm_grpc
from config.config import CONFIG
from service import DockerService

_ONE_DAY_IN_SECONDS = 60 * 60 * 24


class DockerContainerMgrServicer(dcm_grpc.DockerContainerMgrServiceServicer):

    def __init__(self):
        client = docker.from_env()
        self.service = DockerService(client)

    def getContainerIds(self, request: wrappers.BoolValue, context):
        ids = self.service.get_container_ids(show_all=request.value)
        result = dcm.StringList(val=ids)
        return result

    def runContainer(self, request: Empty, context):
        status = self.service.run_container()
        return dcm.ContainerStatus(
            id = status['id'],
            status = status['status'],
            ports = status['ports']
        )

    def stopContainer(self, request: wrappers.StringValue, context):
        id = request.value
        self.service.stop_container_by_id(id)
        return Empty()


    def startContainer(self, request: wrappers.StringValue, context):
        id = request.value
        self.service.start_container_by_id(id)
        return Empty()

    def removeContainer(self, request: wrappers.StringValue, context):
        id = request.value
        self.service.stop_container_by_id(id)
        return Empty()

    def getContainerStatus(self, request: wrappers.StringValue, context):
        id = request.value
        status = self.service.get_container_status(id)
        return dcm.ContainerStatus(
            id=status['id'],
            status=status['status'],
            ports=status['ports']
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=CONFIG['grpc']['max_workers']))
    dcm_grpc.add_DockerContainerMgrServiceServicer_to_server(
        DockerContainerMgrServicer(), server
    )
    server.add_insecure_port('[::]:%s' % CONFIG['grpc']['port'])
    server.start()
    print('start serve on [::]:%s...' % CONFIG['grpc']['port'])
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()