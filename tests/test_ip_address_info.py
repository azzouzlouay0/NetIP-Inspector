import unittest

from src.ip_address_info import IPAddressInfo


class TestIPAddressInfo(unittest.TestCase):

    def test_ipv4_is_parsed(self):
        info = IPAddressInfo("192.168.1.10")
        self.assertEqual(info.version, 4)
        self.assertEqual(info.address, "192.168.1.10")

    def test_ipv6_is_parsed(self):
        info = IPAddressInfo("2001:db8::1")
        self.assertEqual(info.version, 6)
        self.assertEqual(info.address, "2001:db8::1")

    def test_ipv6_is_normalized(self):
        info = IPAddressInfo("2001:0db8:0000:0000:0000:0000:0000:0001")
        self.assertEqual(info.address, "2001:db8::1")

    def test_invalid_address_raises(self):
        for bad in ["abc", "999.1.1.1", "", "1.2.3"]:
            with self.subTest(address=bad):
                with self.assertRaises(ValueError):
                    IPAddressInfo(bad)

    def test_str_representation(self):
        self.assertEqual(str(IPAddressInfo("8.8.8.8")), "IPv4: 8.8.8.8")
        self.assertEqual(str(IPAddressInfo("::1")), "IPv6: ::1")


class TestSubnetDetails(unittest.TestCase):

    def test_slash_24(self):
        d = IPAddressInfo("192.168.1.10").subnet_details(24)
        self.assertEqual(d["ip"], "192.168.1.10")
        self.assertEqual(d["cidr"], "192.168.1.0/24")
        self.assertEqual(d["subnet_mask"], "255.255.255.0")
        self.assertEqual(d["wildcard_mask"], "0.0.0.255")
        self.assertEqual(d["network"], "192.168.1.0")
        self.assertEqual(d["broadcast"], "192.168.1.255")
        self.assertEqual(d["first_host"], "192.168.1.1")
        self.assertEqual(d["last_host"], "192.168.1.254")
        self.assertEqual(d["host_count"], 254)

    def test_slash_16(self):
        d = IPAddressInfo("172.16.5.4").subnet_details(16)
        self.assertEqual(d["cidr"], "172.16.0.0/16")
        self.assertEqual(d["subnet_mask"], "255.255.0.0")
        self.assertEqual(d["host_count"], 65534)

    def test_slash_30(self):
        d = IPAddressInfo("10.0.0.1").subnet_details(30)
        self.assertEqual(d["first_host"], "10.0.0.1")
        self.assertEqual(d["last_host"], "10.0.0.2")
        self.assertEqual(d["host_count"], 2)

    def test_slash_31_has_two_hosts(self):
        d = IPAddressInfo("10.0.0.0").subnet_details(31)
        self.assertEqual(d["first_host"], "10.0.0.0")
        self.assertEqual(d["last_host"], "10.0.0.1")
        self.assertEqual(d["host_count"], 2)

    def test_slash_32_has_one_host(self):
        d = IPAddressInfo("10.0.0.5").subnet_details(32)
        self.assertEqual(d["first_host"], "10.0.0.5")
        self.assertEqual(d["last_host"], "10.0.0.5")
        self.assertEqual(d["host_count"], 1)

    def test_slash_0(self):
        d = IPAddressInfo("1.2.3.4").subnet_details(0)
        self.assertEqual(d["cidr"], "0.0.0.0/0")
        self.assertEqual(d["wildcard_mask"], "255.255.255.255")

    def test_invalid_prefix_raises(self):
        info = IPAddressInfo("192.168.1.1")
        for bad in [33, -1, 99]:
            with self.subTest(prefix=bad):
                with self.assertRaises(ValueError):
                    info.subnet_details(bad)

    def test_ipv6_not_supported(self):
        with self.assertRaises(ValueError):
            IPAddressInfo("2001:db8::1").subnet_details(64)


if __name__ == "__main__":
    unittest.main()
