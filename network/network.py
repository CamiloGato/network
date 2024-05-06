from typing import Dict, List, Any
from networkx import Graph, dijkstra_path, NetworkXNoPath
import networkx as nx
import matplotlib.pyplot as plt
import json


class Network:

    def __init__(self):
        """" Initialize the network Graph """
        self.graph: Graph = Graph()

    def add_edge(self, u: str, v: str, w: int) -> None:
        """Add an edge to the graph with a specified weight if the nodes and weight are valid."""
        if isinstance(w, int) and w > 0:
            self.graph.add_edge(u, v, weight=w)
        else:
            print("Invalid weight; must be a positive integer.")

    def remove_node(self, node: str) -> None:
        """Remove a node from the graph if it exists."""
        if node in self.graph:
            self.graph.remove_node(node)
        else:
            print(f"Node {node} not found in the graph.")

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

    def save_graph(self, filename: str) -> None:
        """Save the graph to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(
                dict(
                    nodes=list(self.graph.nodes()),
                    edges=list(self.graph.edges(data=True))),
                f
            )

    def load_graph(self, filename: str) -> None:
        """Load a graph from a JSON file.

        The JSON file should contain:
        - 'nodes': a list of node identifiers
        - 'edges': a list of tuples (u, v, d) where u and v are node identifiers
          and d is a dictionary of edge attributes, e.g., {'weight': w}.
        """
        try:
            with open(filename, 'r') as f:
                data: Dict[str, Any] = json.load(f)
            self.graph.clear()
            self.graph.add_nodes_from(data['nodes'])
            for u, v, d in data['edges']:
                self.graph.add_edge(u, v, **d)
        except FileNotFoundError:
            print("The graph file does not exist.")
        except json.JSONDecodeError:
            print("Error decoding the graph file.")

    def get_all_routes(self) -> Dict[str, Dict[str, List[str]]]:
        """Calculate all possible routes between all pairs of nodes."""
        all_routes = {}
        for source in self.graph.nodes():
            all_routes[source] = {}
            for target in self.graph.nodes():
                if source != target:
                    try:
                        path: List[str] = dijkstra_path(self.graph, source, target)
                        all_routes[source][target] = path
                    except NetworkXNoPath:
                        all_routes[source][target] = []
                        print(f"No path from {source} to {target}")
                    except Exception as e:
                        all_routes[source][target] = []
                        print(f"Error calculating path from {source} to {target}: {e}")
        return all_routes

    def get_all_routes_json(self) -> str:
        """Get all routes in JSON format."""
        routes: str = json.dumps(self.get_all_routes())
        return routes

    def visualize_graph(self) -> None:
        """Visualize the graph using matplotlib."""
        pos = nx.spring_layout(self.graph)
        nx.draw(
            self.graph,
            pos,
            with_labels=True,
            node_color='skyblue',
            node_size=700,
            edge_color='#FF5733',
            linewidths=1,
            font_size=15
        )
        labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=labels)
        plt.title('Graph')
        plt.show()
