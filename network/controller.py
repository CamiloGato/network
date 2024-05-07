import json
import socket
import time
from socket import socket as Socket
import threading
from typing import Dict, Tuple, List
from network.common.data import DataMessage
from network.common.network import Network
from network.common.tcp_functions import check_connection


class Controller:
    def __init__(self, host: str, port: int, network: Network):
        # Host and network configuration
        self.host: str = host
        self.port: int = port
        self.network: Network = network

        # Socket configuration & clients
        self.server_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Socket, Tuple[str, int]] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print("Server started. Waiting for connections...")
            threading.Thread(target=self.accept_connections).start()
        except Exception as e:
            self.server_socket.close()
            print(f"Server start error: {e}")

    def accept_connections(self) -> None:
        try:
            while True:
                client, address = self.server_socket.accept()
                node: str = f"R{address[1]}"
                with self.lock:
                    self.clients[client] = address
                    self.update_nodes_routes(node, address)

                print(f"Connection established with| R{address[1]} | {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

    def handle_client(self, client: Socket, address: Tuple[str, int]) -> None:
        try:
            while True:
                if not check_connection(client):
                    print(f"Connection Lost - {address}")
                    break

                data: bytes = client.recv(1024)
                if not data:
                    break
                data_decoded: str = data.decode("utf-8")
                data_message: DataMessage = self.process_data(data_decoded)
                print(f"Request received from {address}: {data_message}")

                time.sleep(3)

        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            with self.lock:
                if client in self.clients.keys():
                    node: str = f"R{address[1]}"
                    client.close()
                    del self.clients[client]
                    self.network.remove_route_for(node)
            print(f"Connection closed with {address}")

    def send_routes(self, client: Socket) -> None:
        # routes: str = self.network.get_all_routes_json()
        # client.sendall(routes.encode('utf-8'))
        pass

    def stop(self) -> None:
        self.server_socket.close()
        with self.lock:
            for client in self.clients.keys():
                client.close()
            self.clients.clear()
        print("Controller stopped.")

    def update_nodes_routes(self, node: str, address: Tuple[str, int]):
        self.network.add_node(node, address[0], address[1])
        nodes: List[str] = self.network.get_all_nodes()
        for node in nodes:
            self.network.store_route_for(node)

    def process_data(self, data_encoded: str) -> DataMessage:
        data_message: DataMessage = json.loads(data_encoded)

        return data_message
