from socket import socket as Socket
import socket
import json

from network.common.data import DataMessage


class Client:
    def __init__(self, router_host: str, router_port: int):
        # Client network configuration
        self.router_host: str = router_host
        self.router_port: int = router_port
        self.client: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        try:
            self.client.connect((self.router_host, self.router_port))
            print(f"Connected to the Router {self.router_host}:{self.router_port}")
        except Exception as ex:
            print(f"Failed to connect to the router: {ex}")
            if self.client:
                self.client.close()

    def send_message(self, destination_ip: str, destination_port: int, message: str) -> None:
        try:
            data: DataMessage = DataMessage(
                destination_ip,
                destination_port,
                message,
                []
            )

            json_data = json.dumps(data.__dict__)
            self.client.sendall(json_data.encode('utf-8'))
            print(f"Message sent to {destination_ip}:{destination_port} -> {message}")
        except Exception as ex:
            print(f"Failed to send message: {ex}")

    def receive_message(self) -> DataMessage | None:
        try:
            data = self.client.recv(1024).decode('utf-8')
            data_loaded: DataMessage = json.loads(data)
            return data_loaded
        except Exception as e:
            print(f"Failed to receive message: {e}")
            return None

    def stop(self):
        if self.client:
            self.client.close()
            print("Client Stopped.")
