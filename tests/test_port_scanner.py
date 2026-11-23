import socket
import unittest

from src.port_scanner import PortScanner


class TestInputValidation(unittest.TestCase):

    def test_default_host(self):
        self.assertEqual(PortScanner().host, "127.0.0.1")

    def test_custom_host(self):
        self.assertEqual(PortScanner("10.0.0.1").host, "10.0.0.1")

    def test_invalid_ranges_raise(self):
        scanner = PortScanner()
        bad_ranges = [(0, 10), (10, 5), (1, 65536), (-5, 10), (70000, 80000)]
        for start, end in bad_ranges:
            with self.subTest(start=start, end=end):
                with self.assertRaises(ValueError):
                    scanner.scan(start, end)


class TestWithLocalServer(unittest.TestCase):
    """Opens a real server on localhost so the tests do not need the internet."""

    def setUp(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("127.0.0.1", 0))
        self.server.listen()
        self.open_port = self.server.getsockname()[1]

        # Reserve a free port, then close it so it is guaranteed closed.
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.bind(("127.0.0.1", 0))
        self.closed_port = probe.getsockname()[1]
        probe.close()

    def tearDown(self):
        self.server.close()

    def test_check_port_open(self):
        result = PortScanner().check_port(self.open_port)
        self.assertIsNotNone(result)
        port, service = result
        self.assertEqual(port, self.open_port)
        self.assertIsInstance(service, str)

    def test_check_port_closed_returns_none(self):
        self.assertIsNone(PortScanner().check_port(self.closed_port))

    def test_scan_finds_open_port(self):
        low = max(1, self.open_port - 3)
        high = min(65535, self.open_port + 3)
        found = PortScanner().scan(low, high)
        self.assertIn(self.open_port, [port for port, _ in found])

    def test_scan_single_port_range(self):
        found = PortScanner().scan(self.open_port, self.open_port)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0][0], self.open_port)

    def test_scan_closed_range_is_empty(self):
        found = PortScanner().scan(self.closed_port, self.closed_port)
        self.assertEqual(found, [])

    def test_results_are_port_service_tuples(self):
        found = PortScanner().scan(self.open_port, self.open_port)
        for item in found:
            self.assertEqual(len(item), 2)


if __name__ == "__main__":
    unittest.main()
