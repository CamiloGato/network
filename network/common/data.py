import json
import os
from typing import List, Dict

ROOT_DIR: str = (
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)


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

    @classmethod
    def from_json(cls, json_data: Dict):
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

    @classmethod
    def from_json(cls, json_data: Dict):
        source: DataNode = DataNode.from_json(json_data['source'])
        destination: DataNode = DataNode.from_json(json_data['destination'])
        path: List[DataNode] = [DataNode.from_json(data) for data in json_data['path']]
        return cls(source, destination, path)


class NodeRoutes:
    def __init__(self, node: DataNode, routes: List[DataRoute]):
        self.node: DataNode = node
        self.routes: List[DataRoute] = routes

    def __dict__(self):
        return {
            "node": self.node.__dict__(),
            "routes": [route.__dict__() for route in self.routes]
        }

    @classmethod
    def from_json(cls, json_data: Dict):
        node: DataNode = DataNode.from_json(json_data['node'])
        routes: List[DataRoute] = [DataRoute.from_json(data) for data in json_data['routes']]
        return cls(node, routes)


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

    @classmethod
    def from_json(cls, json_data: Dict):
        destination_ip: str = json_data['destination_ip']
        destination_port: int = json_data['destination_port']
        message: str = json_data['message']
        path: List[DataNode] = [DataNode.from_json(data) for data in json_data['path']]
        return cls(destination_ip, destination_port, message, path)


def store_route(name: str, routes: NodeRoutes):
    filename: str = f"routes_{name}.json"
    file_path: str = os.path.join(ROOT_DIR, "routes", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(routes.__dict__(), f, indent=4)
