from typing import List


class DataNode:
    def __init__(self, name: str, ip: str, port: int):
        self.name: str = name
        self.ip: str = ip
        self.port: int = port

    def __dict__(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "port": self.port
        }


class DataRoute:
    def __init__(self, source: DataNode, destination: DataNode, paths: List[DataNode]):
        self.source: DataNode = source
        self.destination: DataNode = destination
        self.paths: List[DataNode] = paths

    def __dict__(self):
        return {
            "source": self.source.__dict__(),
            "destination": self.destination.__dict__(),
            "path": [path.__dict__() for path in self.paths]
        }


class DataMessage:
    def __init__(self, destination_ip: str, destination_port: int, message: str, path: List[DataNode]):
        self.destination_ip: str = destination_ip
        self.destination_port: int = destination_port
        self.message: str = message
        self.path: List[DataNode] = path

    def __dict__(self):
        return {
            "destination_ip": self.destination_ip,
            "destination_port": self.destination_port,
            "message": self.message,
            "path": [path.__dict__() for path in self.path]
        }
