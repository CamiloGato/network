import socket
import threading
from typing import Dict, Tuple, List
import json

from network.common.data import DataNode, DataRoute, NodeRoutes, store_route
from network.common.utils import debug_log, debug_warning, debug_exception

BUFFER_SIZE = 8192


class Router:
    def __init__(self,
                 controller_host: str,
                 controller_port: int,
                 local_host: str,
                 local_port: int,
                 name: str = "NONE"
                 ) -> None:
        # Name
        self.NAME = f"Router | {name}"

        # Host and network configuration
        self.controller_host: str = controller_host
        self.controller_port: int = controller_port
        self.local_host: str = local_host
        self.local_port: int = local_port
        self.name = name

        # Routes
        self.routes: List[DataRoute] = []

        # Socket client and server
        self.client_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Tuple[str, int], socket.socket] = {}

        # Threading Lock
        self.lock = threading.Lock()
        self.closed = False

        # Routes
        self.routes: NodeRoutes

    def connect_to_controller(self) -> None:
        try:
            self.client_socket.connect((self.controller_host, self.controller_port))
            debug_log(self.NAME,
                      f"Connected to the controller {(self.controller_host, self.controller_port)}")

            # Auth the router
            message_auth = DataNode(
                name=self.name,
                ip=self.local_host,
                port=self.local_port
            )
            json_message = json.dumps(message_auth.__dict__())
            self.client_socket.sendall(json_message.encode('utf-8'))

            threading.Thread(target=self.routes_checker).start()

        except Exception as ex:
            debug_exception(self.NAME,
                            f"Failed to connect to controller: {ex}")

    def routes_checker(self):
        try:
            while True:
                routes: bytes = self.client_socket.recv(BUFFER_SIZE)
                routes_decoded: str = routes.decode('utf-8')
                routes_json: Dict = json.loads(routes_decoded)
                self.routes = NodeRoutes.from_json(routes_json)
                store_route(self.name, self.routes)
        except Exception as ex:
            debug_exception(self.NAME, f"Error Checking Routes: {ex}")

    def start_server(self) -> None:
        self.server_socket.bind((self.local_host, self.local_port))
        self.server_socket.listen(5)
        debug_log(self.NAME, "Router Server Started")
        while not self.closed:
            client, address = self.server_socket.accept()
            debug_log(self.NAME, f"Connection established with {address}")
            with self.lock:
                self.clients[address] = address

            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def handle_client(self, client: socket.socket, address: Tuple[str, int]):
        try:
            data = client.recv(BUFFER_SIZE)
            if data:
                client.sendall(data)
        except Exception as ex:
            debug_exception(self.NAME,
                            f"Error handling client {address}: {ex}")
        finally:
            self.close_client(client, address)

    def close_client(self, client: socket.socket, address: Tuple[str, int]) -> None:
        with self.lock:
            if client in self.clients.values():
                client.close()
                del self.clients[address]
        debug_warning(self.NAME,
                      f"Connection closed with {address}")

    def stop(self) -> None:
        self.closed = True
        self.server_socket.close()
        with self.lock:
            for client in self.clients.values():
                client.close()
            self.clients.clear()
            debug_warning(self.NAME, "Router Server Stopped.")
