import unittest
from unittest.mock import patch, MagicMock
from network.controller import Controller
from network.network import Network


class TestController(unittest.TestCase):
    def setUp(self):
        self.network = Network()
        self.controller = Controller(host='localhost', port=8888, network=self.network)

    @patch('socket.socket')
    def test_start_stop(self, mock_socket):
        server_socket = mock_socket.return_value
        server_socket.accept.side_effect = [Exception("Stop accept loop")]
        with self.assertRaises(Exception):
            self.controller.start()
        self.controller.stop()
        server_socket.close.assert_called()


if __name__ == '__main__':
    unittest.main()
