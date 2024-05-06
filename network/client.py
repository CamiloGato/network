from socket import socket as Socket
import socket
import json


class Client:
    def __init__(self, router_host: str, router_port: int):
        self.router_host: str = router_host
        self.router_port: int = router_port
        self.client: Socket = Socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self) -> None:
        try:
            self.client.connect((self.router_host, self.router_port))
            print(f"Connected to the router {self.router_host}:{self.router_port}")
        except Exception as ex:
            print(f"Failed to connect to the router: {ex}")

    def send_message(self, destination: str, message: str) -> None:
        try:
            data = {"destination": destination, "message": message}
            json_data = json.dumps(data)
            self.client.sendall(json_data.encode('utf-8'))
            print(f"Message sent to {destination}: {message}")
        except Exception as ex:
            print(f"Failed to send message: {ex}")

    def receive_message(self) -> str:
        try:
            data = self.client.recv(1024)
            return data.decode('utf-8')
        except Exception as e:
            print(f"Failed to receive message: {e}")
            return ""

    def stop(self):
        self.client.close()
        print("Client Stopped.")
