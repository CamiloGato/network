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

    def __str__(self) -> str:
        return (f"Node: {self.name} | "
                f"Ip: {self.ip} | "
                f"Port: {self.port}"
                )

    @classmethod
    def from_json(cls, json_data):
        return cls(json_data['name'], json_data['ip'], json_data['port'])


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

    def __str__(self) -> str:
        return (f"Route: Source: {self.source.__str__()} | "
                f"Destination: {self.destination.__str__()} | "
                f"Path: {self.paths.__str__()}"
                )


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

    def __str__(self) -> str:
        return (f"Message: Destination_Ip: {self.destination_ip} | "
                f"Destination_Port: {self.destination_port} | "
                f"Message: {self.message} | "
                f"Path: {self.path.__str__()}"
                )
