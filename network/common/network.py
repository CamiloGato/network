import os
from typing import List
from networkx import Graph, dijkstra_path, NetworkXNoPath

from network.common.data import DataRoute, DataNode
import json

ROOT_DIR: str = (
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )
)


class Network:

    def __init__(self):
        """" Initialize the network Graph """
        self.graph: Graph = Graph()

    def add_edge(self, u: str, v: str, w: int) -> None:
        """ Add an edge to the graph with a specified weight if the nodes and weight are valid. """
        if isinstance(w, int) and w > 0:
            self.graph.add_edge(u, v, weight=w)
        else:
            print(f"Invalid weight {w}; must be a positive integer.")

    def add_node(self, node: DataNode) -> None:
        """" Add nodes to the graph """
        self.graph.add_node(
            node.name,
            ip=node.ip,
            port=node.port
        )

    def remove_node(self, node: DataNode) -> None:
        """Remove a node from the graph if it exists."""
        if node in self.graph:
            self.graph.remove_node(node.name)
        else:
            print(f"Node {node} not found in the graph.")

    def get_all_nodes(self) -> List[str]:
        return self.graph.nodes()

    def shortest_path(self, start: str, end: str) -> list[str]:
        """Find the shortest path from start to end using Dijkstra's algorithm."""
        try:
            return dijkstra_path(self.graph, start, end)
        except NetworkXNoPath:
            print(f"No path found from {start} to {end}.")
            return []
        except Exception as ex:
            print(f"Error calculating path from {start} to {end}: {ex}")
            return []

    def node_to_datanode(self, node: str) -> DataNode:
        """"  """
        node_data = self.graph.nodes[node]

        return DataNode(
            name=node,
            ip=node_data.get("ip"),
            port=node_data.get("port")
        )

    def _generate_data_route(self, source: str, target: str, path: List[str]) -> DataRoute:
        """"  """
        paths_data = [self.node_to_datanode(node) for node in path]
        source_data: DataNode = self.node_to_datanode(source)
        destination_data: DataNode = self.node_to_datanode(target)

        route_data: DataRoute = DataRoute(
            source=source_data,
            destination=destination_data,
            paths=paths_data
        )

        return route_data

    def get_routes_all(self) -> List[DataRoute]:
        """ Calculate all possible routes between all pairs of nodes. """
        all_routes: List[DataRoute] = []
        for source in self.graph.nodes():
            data: List[DataRoute] = self.get_routes_for(source)
            for route in data:
                all_routes.append(route)

        return all_routes

    def get_routes_for(self, node: str) -> List[DataRoute]:
        all_routes: List[DataRoute] = []

        for target in self.graph.nodes():
            if node != target:
                path: List[str] = self.shortest_path(node, target)
                route_data: DataRoute = self._generate_data_route(node, target, path)
                all_routes.append(route_data)

        return all_routes

    def store_route_for(self, node: str):
        routes: List[DataRoute] = self.get_routes_for(node)
        filename: str = f"routes_{node}.json"
        file_path: str = os.path.join(ROOT_DIR, "routes", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump([route.__dict__() for route in routes], f, indent=4)

    def remove_route_for(self, node: str):
        filename: str = f"routes_{node}.json"
        file_path = os.path.join(ROOT_DIR, "routes", filename)

        try:
            os.remove(file_path)
            print(f"Archivo '{filename}' eliminado exitosamente.")
        except FileNotFoundError:
            print(f"El archivo '{filename}' no existe.")
        except Exception as e:
            print(f"Error al eliminar el archivo '{filename}': {e}")
