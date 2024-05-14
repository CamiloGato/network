import json
import threading
import time

from network.common.network import Network
from network.controller import Controller
from network.router import Router

threads = []
routers: list[Router] = []


def create_controller(host: str, port: int, network: Network) -> Controller:
    controller = Controller(host, port, network)
    controller.start_server()
    return controller


def create_router(name: str, host: str, port: int, controller: Controller):
    router = Router(controller.host, controller.port, host, port, name)
    router.connect_to_controller()
    router.start_server()
    routers.append(router)


def main():
    network = Network()

    # Creation of Nodes
    nodes = {
        "WA": ("localhost", 8094),
        "MI": ("localhost", 8081),
        "NY": ("localhost", 8082),
        "CA1": ("localhost", 8083),
        "UT": ("localhost", 8084),
        "CO": ("localhost", 8085),
        "NE": ("localhost", 8086),
        "IL": ("localhost", 8087),
        "PA": ("localhost", 8088),
        "NJ": ("localhost", 8089),
        "CA2": ("localhost", 8090),
        "DC": ("localhost", 8091),
        "TX": ("localhost", 8092),
        "GA": ("localhost", 8093),
    }

    # Creation of Edges
    edges = [
        ("WA", "CA1", 2100),
        ("WA", "CA2", 3000),
        ("WA", "IL", 4800),
        ("CA1", "UT", 1500),
        ("CA1", "CA2", 1200),
        ("CA2", "TX", 3600),
        ("UT", "MI", 3900),
        ("UT", "CO", 1200),
        ("CO", "NE", 1200),
        ("CO", "TX", 2400),
        ("NE", "IL", 1500),
        ("NE", "GA", 2700),
        ("TX", "GA", 1200),
        ("TX", "DC", 3600),
        ("IL", "PA", 1500),
        ("GA", "PA", 1500),
        ("PA", "NY", 600),
        ("PA", "NJ", 600),
        ("MI", "NY", 1200),
        ("MI", "NJ", 1500),
        ("DC", "NY", 600),
        ("DC", "NJ", 300),
    ]

    # Create Controller
    controller = create_controller(
        "localhost",
        8080,
        network
    )

    time.sleep(3)

    for node, (host, port) in nodes.items():
        thread = threading.Thread(target=create_router, args=(node, host, port, controller))
        threads.append(thread)
        thread.start()
        time.sleep(1)

    for (u, v, w) in edges:
        network.add_edge(u, v, w)

    # Store the routes
    routes = network.get_routes_all()
    with open("routes/routes.json", "w") as f:
        json.dump([route.__dict__() for route in routes], f, indent=4)

    print("Routes saved successfully.")
    controller.update_routes()
    print("Updated Routes")

    input("End Execution: ")
    controller.stop()
    for router in routers:
        router.stop()

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
