import unittest
from unittest.mock import patch, MagicMock
import socket
from network.controller import Controller
from network.network import Network
import threading


@patch('socket.socket')
class TestController(unittest.TestCase):

    def setUp(self):
        """Setup the Controller with mocked network and socket."""
        self.network = Network()
        self.host = 'localhost'
        self.port = 12345
        self.controller = Controller(self.host, self.port, self.network)
        self.controller.server_socket = MagicMock()
        self.controller.server_socket.accept = MagicMock(return_value=(MagicMock(), ('127.0.0.1', 12346)))

    def tearDown(self):
        """Ensure all sockets are closed."""
        self.controller.server_socket.close()

    def test_start(self, mock_socket):
        """Test the start method to ensure it binds and listens."""
        self.controller.start()
        self.controller.server_socket.bind.assert_called_with((self.host, self.port))
        self.controller.server_socket.listen.assert_called_with(5)

    # def test_accept_connections(self, mock_socket):
    #     mock_socket.return_value.accept.side_effect = [
    #         (MagicMock(), ('127.0.0.1', 12346)),
    #         socket.error("Forced error to stop the loop")
    #     ]
    #
    #     with patch('threading.Thread') as mock_thread:
    #         with self.assertRaises(socket.error):
    #             self.controller.accept_connections()
    #     mock_thread.assert_called_with(
    #         target=self.controller.handle_client,
    #         args=(MagicMock(), ('127.0.0.1', 12346))
    #     )

    def test_handle_client(self, mock_socket):
        """Test handling of a client sending data."""
        mock_client_socket = MagicMock()
        mock_client_socket.recv = MagicMock(
            side_effect=[b'Hello, world!', b'']  # Simulate client sending data then closing
        )
        self.controller.handle_client(mock_client_socket, ('127.0.0.1', 12346))
        mock_client_socket.sendall.assert_called_once()  # Verify it sends a response

    def test_stop(self, mock_socket):
        """Test the stop method to ensure it closes the server socket and all client sockets."""
        self.controller.clients = {('127.0.0.1', 12346): MagicMock()}
        self.controller.stop()
        self.controller.server_socket.close.assert_called_once()
        for client in self.controller.clients.values():
            client.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
