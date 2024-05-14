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
    def __init__(self, name: str, ip: str, port: int, public_key: str = ""):
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.public_key: str = public_key

    def __dict__(self):
        return {
            "name": self.name,
            "ip": self.ip,
            "port": self.port,
            "public_key": self.public_key,
        }

    @classmethod
    def from_json(cls, json_data: Dict):
        return cls(json_data['name'], json_data['ip'], json_data['port'], json_data['public_key'])


class DataRoute:
    def __init__(self, source: DataNode, destination: DataNode, paths: List[DataNode]):
        self.source: DataNode = source
        self.destination: DataNode = destination
        self.paths: List[DataNode] = paths

    def __dict__(self):
        return {
            "source": self.source.__dict__(),
            "destination": self.destination.__dict__(),
            "path": [DataNode(node.name, node.ip, node.port).__dict__() for node in self.paths]
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

    @classmethod
    def default(cls):
        default_node: DataNode = DataNode("Default", "None", 0, "None")
        default_routes: List[DataRoute] = []
        return cls(default_node, default_routes)


class DataMessage:
    def __init__(self, message: str, path: List[DataNode], key: str = ""):
        self.message: str = message
        self.path: List[DataNode] = path
        self.key: str = key

    def __dict__(self):
        return {
            "message": self.message,
            "path": [path.__dict__() for path in self.path],
            "key": self.key
        }

    def is_current_node(self, node: str) -> bool:
        current_node: DataNode = self.path.pop(0)
        return current_node.name == node

    def is_destine(self, node: str) -> bool:
        return self.path[-1] == node

    def get_current_node(self) -> DataNode:
        return self.path[0]

    @classmethod
    def is_message(cls, message: str) -> bool:
        try:
            message_json: Dict = json.loads(message)
            DataMessage.from_json(message_json)
            return True
        except Exception:
            return False

    @classmethod
    def from_json(cls, json_data: Dict):
        message: str = json_data['message']
        path: List[DataNode] = [DataNode.from_json(data) for data in json_data['path']]
        return cls(message, path)


def store_route(name: str, routes: NodeRoutes):
    filename: str = f"routes_{name}.json"
    file_path: str = os.path.join(ROOT_DIR, "routes", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(routes.__dict__(), f, indent=4)
