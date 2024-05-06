from socket import socket as Socket
import socket

from typing import Dict, Tuple
import json


class Router:
    def __init__(self, controller_host: str, controller_port: int, local_port: int) -> None:
        # Host and network configuration
        self.controller_host: str = controller_host
        self.controller_port: int = controller_port
        self.local_port: int = local_port

        # Socket configuration and clients
        self.routes: Dict[str, Tuple[str, int]] = {}
        self.client_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Tuple[str, int], Socket] = {}

    def connect_to_controller(self) -> None:
        try:
            self.client_socket.connect((self.controller_host, self.controller_port))
            print("Connected to the controller")
            self.client_socket.sendall("Request routes".encode('utf-8'))
            data: str = self.client_socket.recv(4096).decode('utf-8')
            if data:
                self.routes = json.loads(data)
                print("Routes updated")
                self.save_routes()
        except Exception as ex:
            print(f"Failed to connect to controller: {ex}")

    def save_routes(self) -> None:
        with open('routes.json', 'w') as f:
            json.dump(self.routes, f)

    def start_server(self) -> None:
        self.server_socket.bind(('', self.local_port))
        self.server_socket.listen(5)
        print("Router server started. Waiting for connections...")
        while True:
            client, address = self.server_socket.accept()
            print(f"Connection established with {address}")
            client.close()

    def stop(self) -> None:
        self.server_socket.close()
        print("Router stopped.")
