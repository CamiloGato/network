import json
from typing import List

from network.data import DataRoute
from network.network import Network


def main():
    # Crear una red
    network = Network()

    # Agregar nodos con su respectiva dirección IP y puerto (ejemplo genérico)
    nodes = {
        "WA": ("192.168.1.10", 8080),
        "CO": ("192.168.1.14", 8084),
        "NE": ("192.168.1.15", 8085),
    }

    for node, (ip, port) in nodes.items():
        network.add_node(node, ip, port)

    # Agregar aristas con pesos específicos
    edges = [
        ("WA", "CO", 2100), ("CO", "NE", 1200),
        ("WA", "NE", 10000),
    ]

    for u, v, w in edges:
        network.add_edge(u, v, w)

    # Guardar las rutas en un archivo JSON
    routes: List[DataRoute] = network.get_all_routes()
    with open("routes/routes.json", "w") as f:
        json.dump([route.__dict__() for route in routes], f, indent=4)
    print("Routes saved successfully.")

    routes: List[DataRoute] = network.get_routes_for("CO")
    with open("routes/co_routes.json", "w") as f:
        json.dump([route.__dict__() for route in routes], f, indent=4)
    print("Routes saved successfully.")


if __name__ == "__main__":
    main()
