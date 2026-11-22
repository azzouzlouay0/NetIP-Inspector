import socket
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import psutil

from src.network_info import NetworkInfo


def addr(family, address, netmask=None):
    return SimpleNamespace(family=family, address=address, netmask=netmask)


MAC_FAMILY = getattr(psutil, "AF_LINK", None) or getattr(
    socket, "AF_PACKET", None
)


class TestNetworkInfo(unittest.TestCase):

    @patch("src.network_info.psutil.net_if_addrs")
    def test_interface_with_ipv4_and_mac(self, mocked):
        mocked.return_value = {
            "eth0": [
                addr(socket.AF_INET, "192.168.1.5", "255.255.255.0"),
                addr(MAC_FAMILY, "aa:bb:cc:dd:ee:ff"),
            ]
        }
        result = NetworkInfo().get_network_details()
        self.assertEqual(
            result,
            [{
                "interface": "eth0",
                "ipv4": "192.168.1.5",
                "subnet_mask": "255.255.255.0",
                "mac": "aa:bb:cc:dd:ee:ff",
            }],
        )

    @patch("src.network_info.psutil.net_if_addrs")
    def test_interface_without_ipv4_is_skipped(self, mocked):
        mocked.return_value = {
            "lo6": [addr(socket.AF_INET6, "::1")],
            "eth1": [addr(MAC_FAMILY, "aa:bb:cc:dd:ee:ff")],
        }
        self.assertEqual(NetworkInfo().get_network_details(), [])

    @patch("src.network_info.psutil.net_if_addrs")
    def test_interface_without_mac_has_no_mac_key(self, mocked):
        mocked.return_value = {
            "wlan0": [addr(socket.AF_INET, "10.0.0.2", "255.0.0.0")]
        }
        result = NetworkInfo().get_network_details()
        self.assertEqual(len(result), 1)
        self.assertNotIn("mac", result[0])
        self.assertEqual(result[0]["ipv4"], "10.0.0.2")

    @patch("src.network_info.psutil.net_if_addrs")
    def test_multiple_interfaces(self, mocked):
        mocked.return_value = {
            "eth0": [addr(socket.AF_INET, "192.168.1.5", "255.255.255.0")],
            "wlan0": [addr(socket.AF_INET, "10.0.0.2", "255.0.0.0")],
            "down0": [],
        }
        result = NetworkInfo().get_network_details()
        self.assertEqual(
            [item["interface"] for item in result], ["eth0", "wlan0"]
        )

    @patch("src.network_info.psutil.net_if_addrs")
    def test_no_interfaces(self, mocked):
        mocked.return_value = {}
        self.assertEqual(NetworkInfo().get_network_details(), [])

    def test_real_call_returns_well_formed_list(self):
        result = NetworkInfo().get_network_details()
        self.assertIsInstance(result, list)
        for item in result:
            self.assertIn("interface", item)
            self.assertIn("ipv4", item)


if __name__ == "__main__":
    unittest.main()
