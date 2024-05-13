import socket
import threading
from typing import Dict, Tuple, List
import json

from network.common.data import DataNode, DataRoute


class Router:
    def __init__(self,
                 controller_host: str,
                 controller_port: int,
                 local_host: str,
                 local_port: int,
                 name: str = "NONE"
                 ) -> None:

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
        self.clients: Dict[socket.socket, Tuple[str, int]] = {}

        # Threading Lock
        self.lock = threading.Lock()

    def connect_to_controller(self) -> None:
        try:
            self.client_socket.connect((self.controller_host, self.controller_port))
            print(f"Connected to the controller {(self.controller_host, self.controller_port)}")

            message_auth = DataNode(
                name=self.name,
                ip=self.local_host,
                port=self.local_port
            )
            json_message = json.dumps(message_auth.__dict__())
            self.client_socket.sendall(json_message.encode('utf-8'))

            data: str = self.client_socket.recv(4096).decode('utf-8')
            if data:
                routes = json.loads(data)
                print(f"Routes: {routes}")
        except Exception as ex:
            print(f"Failed to connect to controller: {ex}")

    def start_server(self) -> None:
        self.server_socket.bind((self.local_host, self.local_port))
        self.server_socket.listen(5)
        print("Router server started. Waiting for connections...")
        while True:
            client, address = self.server_socket.accept()
            print(f"Connection established with {address}")
            with self.lock:
                self.clients[client] = address
            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def handle_client(self, client: socket.socket, address: Tuple[str, int]):
        try:
            # TODO: Process client requests here
            data = client.recv(1024)
            if data:
                client.sendall(data)
        except Exception as ex:
            print(f"Error handling client {address}: {ex}")
        finally:
            client.close()
            with self.lock:
                if client in self.clients:
                    del self.clients[client]

    def stop(self) -> None:
        with self.lock:
            for client in self.clients.keys():
                client.close()
            self.server_socket.close()
            self.clients.clear()
        print("Router stopped.")
