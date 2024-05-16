import json
import socket
import threading
from typing import Dict, Tuple

from network.common.data import DataNode, DataRoute, NodeRoutes, store_route, DataMessage, read_route_for
from network.common.security import generate_symmetric_key, encrypt_message, generate_keys, serialize_key_public, \
    encrypt_symmetric_key, decrypt_symmetric_key, decrypt_message
from network.common.utils import debug_log, debug_warning, debug_exception

BUFFER_SIZE = 1024 * 1024


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
            public_key = serialize_key_public(self.public_key)
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
        while True:
            try:
                routes = self.controller_socket.recv(BUFFER_SIZE)
                if routes:
                    routes_decoded = routes.decode('utf-8')
                    routes_json = json.loads(routes_decoded)
                    store_route(self.name, NodeRoutes.from_json(routes_json))
                else:
                    debug_warning(self.NAME,
                                  "Received empty route update.")
            except Exception as ex:
                debug_exception(self.NAME,
                                f"Error processing received routes: {ex}")

    def send_message(self, destination: str, message: str, is_file: bool):
        # Find route to destination
        route: DataRoute = read_route_for(self.name, destination)
        if not route:
            debug_warning(self.NAME,
                          f"No route found to {destination}")
            return

        # Generate symmetric key and encrypt message
        sym_key = generate_symmetric_key()
        encrypted_message = encrypt_message(message, sym_key)

        # Get public key of last router and store next_node
        next_node: DataNode = route.paths[1]
        last_node: DataNode = route.paths[-1]
        last_router_public_key: str = last_node.public_key

        if not last_router_public_key:
            debug_warning(self.NAME,
                          f"Last Router Public Key is empty for node {last_node.name}")

        encrypted_sym_key = encrypt_symmetric_key(sym_key, last_router_public_key)

        # Send encrypted message and encrypted symmetric key to next router
        data_message = DataMessage(
            message=encrypted_message,
            path=route.paths[1:],  # Remaining path
            key=encrypted_sym_key,
            is_file=is_file
        )
        json_message = json.dumps(data_message.__dict__())
        try:
            next_node_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            next_node_client_socket.connect((next_node.ip, next_node.port))
            next_node_client_socket.sendall(json_message.encode('utf-8'))
            debug_log(self.NAME,
                      f"Message SENT to {next_node.name}: {json_message}")
            next_node_client_socket.close()
        except Exception as ex:
            debug_exception(self.NAME,
                            f"Failed to send message to {next_node.name}: {ex}")

    def start_server(self) -> None:
        try:
            # Start the binding and socket server.
            self.server_socket.bind((self.local_host, self.local_port))
            self.server_socket.listen(5)
            debug_log(self.NAME,
                      f"Router Server started.")

            threading.Thread(target=self.accept_clients).start()

        except Exception as ex:
            self.server_socket.close()
            debug_exception(self.NAME,
                            f"Router Server start error: {ex}")

    def accept_clients(self):
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                with self.lock:
                    self.clients[address] = client_socket
                debug_log(self.NAME,
                          f"Accepted connection from {address}")
                threading.Thread(target=self.read_messages, args=(client_socket, address)).start()
            except Exception as ex:
                debug_exception(self.NAME,
                                f"Error accepting clients: {ex}")

    def read_messages(self, client_socket: socket.socket, address: Tuple[str, int]):
        try:
            while True:
                data: bytes = client_socket.recv(BUFFER_SIZE)
                if not data:
                    debug_log(self.NAME,
                              f"Connection closed by {address}")
                    break

                message_decoded: str = data.decode('utf-8')
                debug_log(self.NAME,
                          f"Received message: {message_decoded[0:10]}")

                if DataMessage.is_message(message_decoded):
                    message_json: Dict = json.loads(message_decoded)
                    data_message: DataMessage = DataMessage.from_json(message_json)

                    # Check if this router is the current node in the path
                    if data_message.is_current_node(self.name):
                        # Check if this router is the final destination
                        if data_message.is_destine(self.name):
                            enc_message = data_message.message
                            enc_sym_key = data_message.key

                            sym_key = decrypt_symmetric_key(enc_sym_key, self.private_key)
                            message = decrypt_message(enc_message, sym_key)
                            debug_log(self.NAME,
                                      f"Decrypted message: {message}")
                        else:
                            # Get the next node before popping the current node
                            next_node = data_message.path[1] if len(data_message.path) > 1 else None
                            # Pop the current node from the path
                            data_message.path.pop(0)

                            if next_node:
                                json_message = json.dumps(data_message.__dict__())
                                try:
                                    next_node_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                    next_node_client_socket.connect((next_node.ip, next_node.port))
                                    next_node_client_socket.sendall(json_message.encode('utf-8'))
                                    debug_log(self.NAME,
                                              f"Message SENT to {next_node.name}: {json_message}")
                                    next_node_client_socket.close()
                                except Exception as ex:
                                    debug_exception(self.NAME,
                                                    f"Failed to send message to {next_node.name}: {ex}")

                            else:
                                debug_warning(self.NAME,
                                              "No next node found in the path. Message cannot be forwarded.")
                    else:
                        debug_warning(self.NAME,
                                      f"Forbidden Message {data_message.message}")
                else:
                    continue
        except Exception as ex:
            debug_exception(self.NAME,
                            f"Error Reading Messages: {ex}")
        finally:
            self.close_client(client_socket, address)

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
            debug_warning(self.NAME,
                          "Router Server Stopped.")
