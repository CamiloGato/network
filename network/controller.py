import json
import socket
import threading
import time
from typing import Dict, List

from network.common.data import DataNode, DataRoute
from network.common.network import Network
from network.common.tcp_functions import check_connection
from network.common.utils import debug_log, debug_exception, debug_warning


class Controller:
    NAME = "Controller"

    def __init__(self,
                 host: str,
                 port: int,
                 network: Network
                 ) -> None:
        # Host and network configuration
        self.host: str = host
        self.port: int = port
        self.network: Network = network

        # Socket configuration & clients
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[DataNode, socket.socket] = {}

        # Threading Lock
        self.lock = threading.Lock()

    def start_server(self) -> None:
        try:
            # Start the binding and socket server.
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            debug_log(self.NAME, f"Controller started.")

            threading.Thread(target=self.accept_connections).start()

        except Exception as ex:
            self.server_socket.close()
            debug_exception(self.NAME, f"Controller start error: {ex}")

    def accept_connections(self) -> None:
        try:
            while True:
                # Accept connections
                client, address = self.server_socket.accept()
                auth: bytes = client.recv(1024)
                data_decoded: str = auth.decode("utf-8")
                data_auth: Dict = json.loads(data_decoded)
                node: DataNode = DataNode.from_json(data_auth)
                self.add_node(node)
                # self.send_routes(node)

                with self.lock:
                    self.clients[node] = client

                debug_log(self.NAME, f"Connection established with {address}")

                threading.Thread(target=self.client_connection, args=(client, node)).start()
                threading.Thread(target=self.handle_client, args=(client, node)).start()
        except Exception as e:
            debug_exception(self.NAME, f"Error accepting connections: {e}")

    def client_connection(self, client: socket.socket, node: DataNode) -> None:
        try:
            while True:
                if not check_connection(client):
                    debug_warning(self.NAME, f"Connection Lost - {node}")
                    break
                time.sleep(10)
        except Exception as ex:
            debug_exception(self.NAME, f"Error handling connection {node}: {ex}")
        finally:
            self.close_client(client, node)

    def handle_client(self, client: socket.socket, node: DataNode) -> None:
        try:
            while True:
                data: bytes = client.recv(1024)
                if not data:
                    break
                data_decoded: str = data.decode("utf-8")
                data_message: Dict = json.loads(data_decoded)

                debug_log(self.NAME, f"{node.name} sends: {data_message}")

        except Exception as ex:
            debug_exception(self.NAME, f"Error handling client {node.name}: {ex}")

    def send_routes(self, node: DataNode) -> None:
        routes: List[DataRoute] = self.network.get_routes_for(node.name)
        routes_json: str = json.dumps(routes.__dict__())
        client: socket.socket = self.clients[node]
        client.sendall(routes_json.encode('utf-8'))
        pass

    def close_client(self, client: socket.socket, node: DataNode) -> None:
        with self.lock:
            if client in self.clients.values():
                client.close()
                del self.clients[node]
        debug_warning(self.NAME, f"Connection closed with {node.name}")

    def add_node(self, node: DataNode) -> None:
        self.network.add_node(node)

    def close_node(self, node: DataNode) -> None:
        self.network.remove_node(node)

    def stop(self) -> None:
        self.server_socket.close()
        with self.lock:
            for client in self.clients.values():
                client.close()
            self.clients.clear()
        debug_warning(self.NAME, "Controller Stopped.")
