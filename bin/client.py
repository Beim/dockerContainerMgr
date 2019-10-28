import grpc

from proto import dockerContainerMgr_pb2_grpc as dcm_grpc
from config.config import CONFIG
import google.protobuf.wrappers_pb2 as wrappers
from google.protobuf.empty_pb2 import Empty
from proto.dockerContainerMgr_pb2_grpc import DockerContainerMgrServiceStub


def test0(stub: DockerContainerMgrServiceStub):
    bv = wrappers.BoolValue(value=True)
    res = stub.getContainerIds(bv)
    print(res)


def test1(stub: DockerContainerMgrServiceStub):
    containerStatus = stub.runContainer(Empty())
    print(containerStatus)
    pass


def test2(stub: DockerContainerMgrServiceStub):
    res = stub.startContainer(wrappers.StringValue(value="97f6238d4ea1"))
    print(res)


def test3(stub: DockerContainerMgrServiceStub):
    res = stub.getContainerStatus(wrappers.StringValue(value="97f6238d4ea1"))
    print(res)


def run():
    channel = grpc.insecure_channel('119.29.160.85:%s' % CONFIG['grpc']['port'])
    stub = dcm_grpc.DockerContainerMgrServiceStub(channel)
    # test0(stub)
    # test1(stub)
    # test2(stub)
    test3(stub)

if __name__ == '__main__':
    run()