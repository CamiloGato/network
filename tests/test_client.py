import unittest
from unittest.mock import patch, MagicMock
from network.client import Client


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client('localhost', 8887)

    @patch('socket.socket')
    def test_connect(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.connect.return_value = None
        self.client.connect()
        mock_socket_instance.connect.assert_called_with(('localhost', 8887))

    @patch('socket.socket')
    def test_send_message(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.sendall.return_value = None
        self.client.send_message('localhost:9999', 'Hello, World!')
        mock_socket_instance.sendall.assert_called()

    @patch('socket.socket')
    def test_receive_message(self, mock_socket):
        mock_socket_instance = mock_socket.return_value
        mock_socket_instance.recv.return_value = b'Hello, World!'
        message = self.client.receive_message()
        self.assertEqual(message, 'Hello, World!')


if __name__ == '__main__':
    unittest.main()
