import socket
from socket import socket as Socket
import threading
from typing import Dict, Tuple

from .network import Network


class Controller:
    def __init__(self, host: str, port: int, network: Network):
        # Host and network configuration
        self.host: str = host
        self.port: int = port
        self.network: Network = network

        # Socket configuration & clients
        self.server_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Tuple[str, int], Socket] = {}

    def start(self) -> None:
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print("Server started. Waiting for connections...")
            threading.Thread(target=self.accept_connections).start()
        except Exception as e:
            print(f"Server start error: {e}")
            self.server_socket.close()

    def accept_connections(self) -> None:
        try:
            while True:
                client, address = self.server_socket.accept()
                self.clients[address] = client
                print(f"Connection established with {address}")
                threading.Thread(target=self.handle_client, args=(client, address)).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

    def handle_client(self, client: Socket, address: Tuple[str, int]) -> None:
        try:
            while True:
                data: str = client.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Request received from {address}: {data}")
                self.send_routes(client)
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client.close()
            del self.clients[address]
            print(f"Connection closed with {address}")

    def send_routes(self, client: Socket) -> None:
        routes: str = self.network.get_all_routes_json()
        client.sendall(routes.encode('utf-8'))

    def stop(self) -> None:
        for client in self.clients.values():
            client.close()
        self.server_socket.close()
        print("Controller stopped.")
