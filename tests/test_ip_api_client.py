import unittest
from unittest.mock import MagicMock

import requests

from src.ip_address_info import IPAddressInfo
from src.ip_api_client import IPApiClient


def fake_session(payload=None, error=None):
    """Build a fake requests session so no real network call is made."""
    response = MagicMock()
    response.json.return_value = payload
    if error is not None:
        response.raise_for_status.side_effect = error
    session = MagicMock()
    session.get.return_value = response
    return session


class TestPublicIP(unittest.TestCase):

    def test_get_ipv4(self):
        session = fake_session({"ip": "8.8.8.8"})
        info = IPApiClient(session=session).get_ipv4()
        self.assertIsInstance(info, IPAddressInfo)
        self.assertEqual(info.address, "8.8.8.8")
        self.assertEqual(info.version, 4)
        session.get.assert_called_once_with(
            IPApiClient.IPV4_URL, timeout=5.0
        )

    def test_get_ipv6(self):
        session = fake_session({"ip": "2001:db8::1"})
        info = IPApiClient(session=session).get_ipv6()
        self.assertEqual(info.version, 6)
        session.get.assert_called_once_with(
            IPApiClient.IPV6_URL, timeout=5.0
        )

    def test_custom_timeout_is_used(self):
        session = fake_session({"ip": "8.8.8.8"})
        IPApiClient(timeout=2.0, session=session).get_ipv4()
        session.get.assert_called_once_with(
            IPApiClient.IPV4_URL, timeout=2.0
        )

    def test_missing_ip_key_raises(self):
        client = IPApiClient(session=fake_session({"hello": "world"}))
        with self.assertRaises(ValueError):
            client.get_ipv4()

    def test_non_dict_response_raises(self):
        client = IPApiClient(session=fake_session(["8.8.8.8"]))
        with self.assertRaises(ValueError):
            client.get_ipv4()

    def test_invalid_ip_in_response_raises(self):
        client = IPApiClient(session=fake_session({"ip": "not-an-ip"}))
        with self.assertRaises(ValueError):
            client.get_ipv4()

    def test_http_error_is_propagated(self):
        session = fake_session(
            {"ip": "8.8.8.8"}, error=requests.HTTPError("500")
        )
        with self.assertRaises(requests.HTTPError):
            IPApiClient(session=session).get_ipv4()

    def test_network_failure_is_propagated(self):
        session = MagicMock()
        session.get.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(requests.ConnectionError):
            IPApiClient(session=session).get_ipv4()

    def test_timeout_is_propagated(self):
        session = MagicMock()
        session.get.side_effect = requests.Timeout("too slow")
        with self.assertRaises(requests.Timeout):
            IPApiClient(session=session).get_ipv6()


class TestLocation(unittest.TestCase):

    PAYLOAD = {
        "success": True,
        "ip": "8.8.8.8",
        "country": "United States",
        "region": "California",
        "city": "Mountain View",
        "latitude": 37.4,
        "longitude": -122.0,
        "connection": {"isp": "Google LLC"},
    }

    def test_location_for_given_ip(self):
        session = fake_session(dict(self.PAYLOAD))
        data = IPApiClient(session=session).get_location("8.8.8.8")
        self.assertEqual(data["country"], "United States")
        self.assertEqual(data["city"], "Mountain View")
        self.assertEqual(data["isp"], "Google LLC")
        self.assertEqual(data["latitude"], 37.4)
        session.get.assert_called_once_with(
            IPApiClient.LOCATION_URL + "8.8.8.8", timeout=5.0
        )

    def test_location_without_ip_uses_own_ipv4(self):
        session = MagicMock()
        first = MagicMock()
        first.json.return_value = {"ip": "8.8.8.8"}
        second = MagicMock()
        second.json.return_value = dict(self.PAYLOAD)
        session.get.side_effect = [first, second]

        data = IPApiClient(session=session).get_location()

        self.assertEqual(data["ip"], "8.8.8.8")
        self.assertEqual(session.get.call_count, 2)

    def test_missing_fields_default_to_unknown(self):
        session = fake_session({"success": True, "ip": "8.8.8.8"})
        data = IPApiClient(session=session).get_location("8.8.8.8")
        self.assertEqual(data["country"], "Unknown")
        self.assertEqual(data["region"], "Unknown")
        self.assertEqual(data["city"], "Unknown")
        self.assertEqual(data["isp"], "Unknown")
        self.assertIsNone(data["latitude"])

    def test_null_connection_is_handled(self):
        session = fake_session(
            {"success": True, "ip": "8.8.8.8", "connection": None}
        )
        data = IPApiClient(session=session).get_location("8.8.8.8")
        self.assertEqual(data["isp"], "Unknown")

    def test_failed_lookup_raises(self):
        session = fake_session({"success": False, "message": "Invalid IP"})
        with self.assertRaises(ValueError):
            IPApiClient(session=session).get_location("8.8.8.8")

    def test_non_dict_location_response_raises(self):
        session = fake_session("oops")
        with self.assertRaises(ValueError):
            IPApiClient(session=session).get_location("8.8.8.8")

    def test_invalid_ip_argument_raises_before_request(self):
        session = MagicMock()
        with self.assertRaises(ValueError):
            IPApiClient(session=session).get_location("bad-ip")
        session.get.assert_not_called()

    def test_http_error_on_location_is_propagated(self):
        session = fake_session(
            dict(self.PAYLOAD), error=requests.HTTPError("429")
        )
        with self.assertRaises(requests.HTTPError):
            IPApiClient(session=session).get_location("8.8.8.8")


if __name__ == "__main__":
    unittest.main()
