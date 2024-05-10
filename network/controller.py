import json
import socket
import threading
import time
from socket import socket as Socket
from typing import Dict, Tuple

from network.common.data import DataMessage, DataNode
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
                with self.lock:
                    self.clients[client] = address

                print(f"Connection established with| R{address[1]} | {address[0]}:{address[1]}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
                threading.Thread(target=self.client_connection, args=(client, address)).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

    def client_connection(self, client: Socket, address: Tuple[str, int]) -> None:
        try:
            while True:
                if not check_connection(client):
                    print(f"Connection Lost - {address}")
                    break
                time.sleep(3)
        except Exception as ex:
            print(f"Error handling client {address}: {ex}")
        finally:
            self.close_client(client, address)

    def handle_client(self, client: Socket, address: Tuple[str, int]) -> None:
        try:
            auth: bytes = client.recv(1024)
            data_decoded: str = auth.decode("utf-8")
            data_auth: DataNode = json.loads(data_decoded)
            print(data_auth)
            self.add_node(data_auth)

            while True:
                data: bytes = client.recv(1024)
                if not data:
                    break
                data_decoded: str = data.decode("utf-8")
                data_message: DataMessage = json.loads(data_decoded)
                print(f"Request received from {address}: {data_message}")

        except Exception as ex:
            print(f"Error handling client {address}: {ex}")

    # def send_routes(self, client: Socket, address: Tuple[str, int]) -> None:
    #     routes: List[DataRoute] = self.network.get_routes_for()
    #
    #     client.sendall(routes.encode('utf-8'))
    #     pass

    def close_client(self, client: Socket, address: Tuple[str, int]) -> None:
        with self.lock:
            if client in self.clients.keys():
                client.close()
                del self.clients[client]
        print(f"Connection closed with {address}")

    def add_node(self, node: DataNode) -> None:
        self.network.add_node(node.name, node.ip, node.port)
        pass

    def close_node(self, node: DataNode) -> None:
        self.network.remove_node(node.name)
        pass

    def stop(self) -> None:
        self.server_socket.close()
        with self.lock:
            for client in self.clients.keys():
                client.close()
            self.clients.clear()
        print("Controller stopped.")
