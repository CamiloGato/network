import json
import socket
from socket import socket as Socket
import threading
from typing import Dict, Tuple, Any
from .data import DataMessage
from .network import Network


class Controller:
    def __init__(self, host: str, port: int, network: Network):
        # Host and network configuration
        self.host: str = host
        self.port: int = port
        self.network: Network = network

        # Socket configuration & clients
        self.server_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Socket, Any] = {}
        self.lock = threading.Lock()

    def start(self) -> None:
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print("Server started. Waiting for connections...")
            threading.Thread(target=self.accept_connections, daemon=True).start()
        except Exception as e:
            self.server_socket.close()
            print(f"Server start error: {e}")

    def accept_connections(self) -> None:
        try:
            while True:
                client, address = self.server_socket.accept()
                with self.lock:
                    self.clients[client] = address
                print(f"Connection established with {address}")
                threading.Thread(target=self.handle_client, args=(client, address), daemon=True).start()
        except Exception as e:
            print(f"Error accepting connections: {e}")

    def handle_client(self, client: Socket, address: Tuple[str, int]) -> None:
        try:
            while True:
                data: bytes = client.recv(1024)
                if not data:
                    break
                data_decoded: str = data.decode("utf-8")
                data_message: DataMessage = json.loads(data_decoded)

                print(f"Request received from {address}: {data}")
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            with self.lock:
                if client in self.clients.keys():
                    client.close()
                    del self.clients[client]
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
