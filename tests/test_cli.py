import io
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

from src.cli import CLI


def output_of(func, *args):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = func(*args)
    return buffer.getvalue(), result


class TestMenu(unittest.TestCase):

    def setUp(self):
        self.cli = CLI()

    def test_menu_has_title_and_all_options(self):
        menu = self.cli._build_menu()
        self.assertIn("NETIP-INSPECTOR", menu)
        for option in CLI.OPTIONS:
            self.assertIn(option, menu)

    def test_menu_contains_exit_option(self):
        self.assertIn("0. Exit", self.cli._build_menu())

    def test_menu_lines_are_not_wider_than_width(self):
        for line in self.cli._build_menu().splitlines():
            self.assertLessEqual(len(line), CLI.WIDTH)

    def test_menu_borders_use_full_width(self):
        lines = self.cli._build_menu().splitlines()
        self.assertEqual(lines[0], "=" * CLI.WIDTH)
        self.assertEqual(lines[-1], "=" * CLI.WIDTH)

    def test_title_is_centered(self):
        title_line = self.cli._build_menu().splitlines()[1]
        self.assertEqual(title_line, "NETIP-INSPECTOR".center(CLI.WIDTH))

    def test_ask_choice_returns_stripped_input(self):
        with patch("builtins.input", return_value="  3  "):
            _, choice = output_of(self.cli.ask_choice)
        self.assertEqual(choice, "3")

    def test_ask_choice_prints_menu(self):
        with patch("builtins.input", return_value="0"):
            printed, _ = output_of(self.cli.ask_choice)
        self.assertIn("NETIP-INSPECTOR", printed)

    def test_ask_choice_shows_prompt(self):
        with patch("builtins.input", return_value="1") as mocked:
            output_of(self.cli.ask_choice)
        mocked.assert_called_once_with("Enter your choice: ")


class TestDisplays(unittest.TestCase):

    def setUp(self):
        self.cli = CLI()

    def test_show_ip_v4(self):
        info = SimpleNamespace(version=4, address="1.2.3.4")
        printed, _ = output_of(self.cli.show_ip, info)
        self.assertEqual(printed, "IPv4 public address: 1.2.3.4\n")

    def test_show_ip_v6(self):
        info = SimpleNamespace(version=6, address="::1")
        printed, _ = output_of(self.cli.show_ip, info)
        self.assertEqual(printed, "IPv6 public address: ::1\n")

    def test_show_location(self):
        data = {"country": "Tunisia", "isp": "Test ISP", "city": "Tunis"}
        printed, _ = output_of(self.cli.show_location, data)
        self.assertIn("=== IP GEOLOCATION ===", printed)
        self.assertIn("Country: Tunisia", printed)
        self.assertIn("ISP: Test ISP", printed)
        self.assertIn("City: Tunis", printed)

    def test_acronym_labels_are_uppercase(self):
        data = {"ip": "1.1.1.1", "cidr": "1.1.1.0/24", "mac": "aa:bb"}
        printed, _ = output_of(self.cli.show_subnet, data)
        self.assertIn("IP: 1.1.1.1", printed)
        self.assertIn("CIDR: 1.1.1.0/24", printed)
        self.assertIn("MAC: aa:bb", printed)
        self.assertNotIn("Ip:", printed)
        self.assertNotIn("Cidr:", printed)

    def test_show_subnet_formats_keys(self):
        data = {"subnet_mask": "255.255.255.0", "host_count": 254}
        printed, _ = output_of(self.cli.show_subnet, data)
        self.assertIn("=== SUBNET INFORMATION ===", printed)
        self.assertIn("Subnet Mask: 255.255.255.0", printed)
        self.assertIn("Host Count: 254", printed)

    def test_show_local_network(self):
        data = {"interface": "eth0", "ipv4": "192.168.1.5"}
        printed, _ = output_of(self.cli.show_local_network, data)
        self.assertIn("=== LOCAL NETWORK ===", printed)
        self.assertIn("Interface: eth0", printed)
        self.assertIn("IPv4: 192.168.1.5", printed)

    def test_show_ports_with_results(self):
        printed, _ = output_of(
            self.cli.show_ports, [(22, "ssh"), (80, "http")]
        )
        self.assertIn("=== OPEN TCP PORTS ===", printed)
        self.assertIn("Total open ports: 2", printed)
        self.assertIn("Port 22: ssh", printed)
        self.assertIn("Port 80: http", printed)

    def test_show_ports_empty(self):
        printed, _ = output_of(self.cli.show_ports, [])
        self.assertIn("Total open ports: 0", printed)
        self.assertNotIn("Port ", printed.replace("Total open ports", ""))

    def test_show_error(self):
        printed, _ = output_of(self.cli.show_error, "boom")
        self.assertEqual(printed, "Error: boom\n")

    def test_show_error_with_exception(self):
        printed, _ = output_of(self.cli.show_error, ValueError("bad"))
        self.assertEqual(printed, "Error: bad\n")

    def test_show_report_full(self):
        report = {
            "ipv4": SimpleNamespace(version=4, address="1.2.3.4"),
            "ipv6": SimpleNamespace(version=6, address="::1"),
            "location": {"country": "Tunisia", "isp": "Test ISP"},
            "networks": [
                {"interface": "eth0", "ipv4": "10.0.0.2"},
                {"interface": "wlan0", "ipv4": "10.0.0.3"},
            ],
            "ports": [(80, "http")],
            "errors": ["IPv6 not available"],
        }
        printed, _ = output_of(self.cli.show_report, report)
        self.assertIn("FULL NETWORK REPORT", printed)
        self.assertIn("IPv4 public address: 1.2.3.4", printed)
        self.assertIn("IPv6 public address: ::1", printed)
        self.assertIn("Country: Tunisia", printed)
        self.assertIn("Interface: eth0", printed)
        self.assertIn("Interface: wlan0", printed)
        self.assertIn("Port 80: http", printed)
        self.assertIn("Error: IPv6 not available", printed)

    def test_show_report_with_missing_sections(self):
        printed, _ = output_of(self.cli.show_report, {})
        self.assertIn("FULL NETWORK REPORT", printed)
        self.assertNotIn("OPEN TCP PORTS", printed)
        self.assertNotIn("Error:", printed)

    def test_show_message(self):
        printed, _ = output_of(self.cli.show_message, "hello")
        self.assertEqual(printed, "hello\n")


if __name__ == "__main__":
    unittest.main()
