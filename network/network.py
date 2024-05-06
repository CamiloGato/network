from typing import Dict, List

from networkx import Graph, dijkstra_path, NetworkXNoPath
import json


class Network:

    def __init__(self):
        self.graph: Graph = Graph()

    def add_edge(self, u: str, v: str, w: int) -> None:
        self.graph.add_edge(u, v, weight=w)

    def remove_node(self, node: str) -> None:
        if node in self.graph:
            self.graph.remove_node(node)

    def shortest_path(self, start: str, end: str) -> list[str]:
        path: list[str]
        try:
            path = dijkstra_path(self.graph, start, end)
        except Exception as ex:
            print(f"Error calculating path: {ex}")
            path = []

        return path

    def save_graph(self) -> None:
        with open('network_graph.json', 'w') as f:
            json.dump(
                dict(
                    nodes=list(self.graph.nodes()),
                    edges=list(self.graph.edges(data=True))),
                f
            )

    def load_graph(self) -> None:
        with open('network_graph.json', 'r') as f:
            data: dict[str, str] = json.load(f)
            self.graph = Graph()
            self.graph.add_nodes_from(data['nodes'])
            self.graph.add_weighted_edges_from((u, v, d['weight']) for u, v, d in data['edges'])

    def get_all_routes(self) -> Dict[str, Dict[str, List[str]]]:
        all_routes: Dict[str, Dict[str, List[str]]] = {}
        for source in self.graph.nodes():
            all_routes[source] = {}
            for target in self.graph.nodes():
                if source != target:
                    try:
                        path: List[str] = dijkstra_path(self.graph, source, target)
                        all_routes[source][target] = path
                    except NetworkXNoPath:
                        print(f"No path from {source} to {target}")
                    except Exception as e:
                        print(f"Error calculating path from {source} to {target}: {e}")
        return all_routes

    def get_all_routes_json(self) -> str:
        routes: str = json.dumps(self.get_all_routes())
        return routes
