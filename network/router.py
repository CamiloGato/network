import json
import socket
import threading
from typing import Dict, Tuple

from network.common.data import DataNode, DataRoute, NodeRoutes, store_route, DataMessage
from network.common.security import generate_symmetric_key, encrypt_message, generate_keys, serialize_key_public, \
    encrypt_symmetric_key, decrypt_symmetric_key, decrypt_message
from network.common.utils import debug_log, debug_warning, debug_exception

BUFFER_SIZE = 655360


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

        # Socket client/server configuration and clients
        self.controller_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[Tuple[str, int], socket.socket] = {}

        # Routes
        self.routes: NodeRoutes = NodeRoutes.default()

        # Security Keys
        self.private_key, self.public_key = generate_keys()

        # Threading Lock
        self.lock = threading.Lock()

    def connect_to_controller(self) -> None:
        try:
            self.controller_socket.connect((self.controller_host, self.controller_port))
            debug_log(self.NAME,
                      f"Connected to the controller {(self.controller_host, self.controller_port)}")

            # Auth the router
            public_key = serialize_key_public(self.public_key).decode()
            message_auth = DataNode(
                name=self.name,
                ip=self.local_host,
                port=self.local_port,
                public_key=public_key
            )
            json_message = json.dumps(message_auth.__dict__())
            self.controller_socket.sendall(json_message.encode('utf-8'))

            threading.Thread(target=self.routes_checker).start()

        except Exception as ex:
            debug_exception(self.NAME,
                            f"Failed to connect to controller: {ex}")

    def routes_checker(self):
        try:
            while True:
                routes: bytes = self.controller_socket.recv(BUFFER_SIZE)
                routes_decoded: str = routes.decode('utf-8')
                routes_json: Dict = json.loads(routes_decoded)
                self.routes = NodeRoutes.from_json(routes_json)
                store_route(self.name, self.routes)
        except Exception as ex:
            debug_exception(self.NAME, f"Error Checking Routes: {ex}")

    def send_message(self, destination: str, message: str):
        # Find route to destination
        route: DataRoute = next((r for r in self.routes.routes if r.destination.name == destination), None)
        if not route:
            debug_warning(self.NAME, f"No route found to {destination}")
            return

        # Generate symmetric key and encrypt message
        sym_key = generate_symmetric_key()
        encrypted_message = encrypt_message(message, sym_key)

        # Get public key of next router
        next_node: DataNode = route.paths[1]
        next_router_public_key: str = next_node.public_key
        encrypted_sym_key = encrypt_symmetric_key(sym_key, next_router_public_key)

        # Send encrypted message and encrypted symmetric key to next router
        data_message = DataMessage(
            encrypted_message,
            route.paths[1::],
            encrypted_sym_key
        )
        json_message = json.dumps(data_message.__dict__())
        next_node_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        next_node_client_socket.connect((next_node.ip, next_node.port))
        next_node_client_socket.sendall(json_message.encode('utf-8'))
        next_node_client_socket.close()

    def start_server(self) -> None:
        try:
            # Start the binding and socket server.
            self.server_socket.bind((self.local_host, self.local_port))
            self.server_socket.listen(5)
            debug_log(self.NAME, f"Router Server started.")

            threading.Thread(target=self.handle_client).start()
            threading.Thread(target=self.read_messages).start()

        except Exception as ex:
            self.server_socket.close()
            debug_exception(self.NAME, f"Router Server start error: {ex}")

    def handle_client(self):
        pass

    def read_messages(self):
        while True:
            data: bytes = self.controller_socket.recv(BUFFER_SIZE)
            if data:
                message_decoded: str = data.decode('utf-8')
                if DataMessage.is_message(message_decoded):
                    message_json: Dict = json.loads(message_decoded)
                    data_message: DataMessage = DataMessage.from_json(message_json)
                    if data_message.is_current_node(self.name):
                        if data_message.is_destine(self.name):
                            enc_message = data_message.message
                            enc_sym_key = data_message.key

                            sym_key = decrypt_symmetric_key(enc_sym_key, self.private_key)
                            message = decrypt_message(enc_message, sym_key)
                            debug_log(self.NAME, f"Message: {message}")
                        else:
                            next_node: DataNode = data_message.get_current_node()
                            json_message = json.dumps(data_message.__dict__())
                            next_node_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            next_node_client_socket.connect((next_node.ip, next_node.port))
                            next_node_client_socket.sendall(json_message.encode('utf-8'))
                            next_node_client_socket.close()
                    else:
                        debug_warning(self.NAME, f"Forbidden Message {data_message.message}")
                else:
                    continue

    def close_client(self, client: socket.socket, address: Tuple[str, int]) -> None:
        with self.lock:
            if client in self.clients.values():
                client.close()
                del self.clients[address]
        debug_warning(self.NAME,
                      f"Connection closed with {address}")

    def stop(self) -> None:
        self.server_socket.close()
        with self.lock:
            for client in self.clients.values():
                client.close()
            self.clients.clear()
            debug_warning(self.NAME, "Router Server Stopped.")
