import unittest
from unittest.mock import MagicMock, patch
from network.router import Router


class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router = Router('localhost', 8888, 8887)

    @patch('socket.socket')
    def test_connection_to_controller(self, mock_socket):
        client_socket = mock_socket.return_value
        self.router.connect_to_controller()
        client_socket.connect.assert_called_with(('localhost', 8888))


if __name__ == '__main__':
    unittest.main()
