import unittest
from network.network import Network
import tempfile
import os


class TestNetwork(unittest.TestCase):

    def setUp(self):
        """Setup for each test case."""
        self.network = Network()
        # Create a temporary file to use for testing save/load functionality
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)

    def tearDown(self):
        """Cleanup after tests."""
        # Close and remove the temporary file
        self.temp_file.close()
        os.unlink(self.temp_file.name)

    def test_add_edge(self):
        """Test adding an edge and verifying it exists in the graph."""
        self.network.add_edge('A', 'B', 10)
        self.assertTrue(('A', 'B') in self.network.graph.edges())
        self.assertEqual(self.network.graph['A']['B']['weight'], 10)

    def test_remove_node(self):
        """Test removing a node and ensuring it is no longer in the graph."""
        self.network.add_edge('A', 'B', 10)
        self.network.remove_node('A')
        self.assertNotIn('A', self.network.graph.nodes())

    def test_shortest_path(self):
        """Test finding the shortest path between two nodes."""
        self.network.add_edge('A', 'B', 10)
        self.network.add_edge('B', 'C', 5)
        self.network.add_edge('A', 'C', 20)
        path = self.network.shortest_path('A', 'C')
        self.assertEqual(path, ['A', 'B', 'C'])

    def test_save_load_graph(self):
        """Test saving a graph to a file and then loading it using a tempfile."""
        self.network.add_edge('A', 'B', 10)
        self.network.add_edge('B', 'C', 5)
        self.network.save_graph(self.temp_file.name)  # Save to the tempfile
        self.network.graph.clear()  # Clear the graph to simulate reloading
        self.network.load_graph(self.temp_file.name)  # Load from the tempfile
        self.assertTrue(('A', 'B') in self.network.graph.edges())
        self.assertEqual(self.network.graph['A']['B']['weight'], 10)
        self.assertTrue(('B', 'C') in self.network.graph.edges())
        self.assertEqual(self.network.graph['B']['C']['weight'], 5)


if __name__ == '__main__':
    unittest.main()
