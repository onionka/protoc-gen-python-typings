# ############################################################################# #
#  Automatically generated protobuf stub files for python                       #
#   by protoc-gen-python_grpc_typings plugin for protoc                         #
# ############################################################################# #

from abc import ABC, abstractmethod
from application_pb2 import *
from grpc import ServicerContext, Channel, Server


class UserMortgageServiceStub(object):
    def __init__(self, channel: Channel):
        pass

    def Check(self, request: SimpleMessage, timeout: int = 0) -> SimpleMessage:
        pass

    def Check2(self, request: SimpleMessage, timeout: int = 0) -> SimpleMessage:
        pass


class UserMortgageServiceServicer(ABC):
    @abstractmethod    
    def Check(self, request: SimpleMessage, context: ServicerContext) -> SimpleMessage:
        pass

    @abstractmethod    
    def Check2(self, request: SimpleMessage, context: ServicerContext) -> SimpleMessage:
        pass


def add_UserMortgageServiceServicer_to_server(servicer: UserMortgageServiceServicer, server: Server):
    pass
