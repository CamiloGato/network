import unittest
from network.network import Network


class TestNetwork(unittest.TestCase):
    def setUp(self):
        self.network = Network()
        self.network.add_edge('A', 'B', 1)
        self.network.add_edge('B', 'C', 2)
        self.network.add_edge('A', 'C', 4)

    def test_shortest_path(self):
        path = self.network.shortest_path('A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'])

    def test_no_path(self):
        self.network.remove_node('C')
        path = self.network.shortest_path('B', 'C')
        self.assertEqual(path, [])


if __name__ == '__main__':
    unittest.main()
