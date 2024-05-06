import unittest
from unittest.mock import patch, MagicMock
from network.router import Router
import socket
import threading


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router("192.168.1.1", 5000, 6000)

    @patch('socket.socket')
    def test_connect_to_controller(self, mock_socket):
        mock_socket.return_value.recv.return_value = b'{"route1": ["192.168.1.2", 6001]}'
        self.router.connect_to_controller()

        mock_socket.return_value.connect.assert_called_with(("192.168.1.1", 5000))
        mock_socket.return_value.sendall.assert_called_with("Request routes".encode('utf-8'))
        self.assertIn("route1", self.router.routes)

    @patch('builtins.open', unittest.mock.mock_open())
    @patch('json.dump')
    def test_save_routes(self, mock_json_dump):
        self.router.routes = {"route1": ("192.168.1.2", 6001)}
        self.router.save_routes()
        mock_json_dump.assert_called_once()

    @patch('socket.socket')
    def test_start_server(self, mock_socket):
        mock_socket.return_value.accept.return_value = (MagicMock(), ('192.168.1.100', 5001))
        with patch('threading.Thread') as mock_thread:
            self.router.start_server()
            mock_socket.return_value.bind.assert_called_with(('', 6000))
            mock_socket.return_value.listen.assert_called_with(5)
            mock_thread.assert_called()

    @patch('socket.socket')
    def test_handle_client(self, mock_socket):
        client_socket = MagicMock()
        client_address = ('192.168.1.100', 5001)
        self.router.clients[client_address] = client_socket
        client_socket.recv.return_value = b'Hello World'
        self.router.handle_client(client_socket, client_address)
        client_socket.sendall.assert_called_with(b'Hello World')
        self.assertNotIn(client_address, self.router.clients)

    def test_stop(self):
        self.router.clients = {('192.168.1.100', 5001): MagicMock()}
        self.router.server_socket = MagicMock()
        self.router.stop()
        self.router.server_socket.close.assert_called_once()
        for client in self.router.clients.values():
            client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
