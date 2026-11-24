import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock

import requests

from src.ip_address_info import IPAddressInfo
from src.ip_api_client import IPApiClient, IPApiError


def fake_session(payload=None, error=None):
    """Build a fake requests session so no real network call is made."""
    response = MagicMock()
    response.json.return_value = payload
    if error is not None:
        response.raise_for_status.side_effect = error
    session = MagicMock()
    session.get.return_value = response
    return session


def http_error(status_code):
    return requests.HTTPError(
        f"{status_code} error",
        response=SimpleNamespace(status_code=status_code),
    )


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

    def test_api_error_is_an_exception(self):
        self.assertTrue(issubclass(IPApiError, Exception))

    def test_missing_ip_key_raises(self):
        client = IPApiClient(session=fake_session({"hello": "world"}))
        with self.assertRaisesRegex(IPApiError, "missing IP address"):
            client.get_ipv4()

    def test_ip_that_is_not_a_string_raises(self):
        client = IPApiClient(session=fake_session({"ip": 12345}))
        with self.assertRaisesRegex(IPApiError, "missing IP address"):
            client.get_ipv4()

    def test_non_dict_response_raises(self):
        client = IPApiClient(session=fake_session(["8.8.8.8"]))
        with self.assertRaisesRegex(IPApiError, "invalid JSON response"):
            client.get_ipv4()

    def test_invalid_ip_in_response_raises(self):
        client = IPApiClient(session=fake_session({"ip": "not-an-ip"}))
        with self.assertRaisesRegex(IPApiError, "invalid IP address"):
            client.get_ipv4()

    def test_ipv6_returned_by_ipv4_endpoint_raises(self):
        client = IPApiClient(session=fake_session({"ip": "2001:db8::1"}))
        with self.assertRaisesRegex(IPApiError, "incorrect IP version"):
            client.get_ipv4()

    def test_ipv4_returned_by_ipv6_endpoint_raises(self):
        client = IPApiClient(session=fake_session({"ip": "8.8.8.8"}))
        with self.assertRaisesRegex(IPApiError, "incorrect IP version"):
            client.get_ipv6()

    def test_http_error_becomes_api_error_with_status(self):
        session = fake_session({"ip": "8.8.8.8"}, error=http_error(500))
        with self.assertRaisesRegex(IPApiError, "HTTP error 500"):
            IPApiClient(session=session).get_ipv4()

    def test_network_failure_becomes_api_error(self):
        session = MagicMock()
        session.get.side_effect = requests.ConnectionError("offline")
        with self.assertRaisesRegex(IPApiError, "network connection failed"):
            IPApiClient(session=session).get_ipv4()

    def test_timeout_becomes_api_error(self):
        session = MagicMock()
        session.get.side_effect = requests.Timeout("too slow")
        with self.assertRaisesRegex(IPApiError, "timed out"):
            IPApiClient(session=session).get_ipv6()

    def test_invalid_json_becomes_api_error(self):
        response = MagicMock()
        response.json.side_effect = ValueError("not json")
        session = MagicMock()
        session.get.return_value = response
        with self.assertRaisesRegex(IPApiError, "invalid response"):
            IPApiClient(session=session).get_ipv4()

    def test_other_request_errors_become_api_error(self):
        session = MagicMock()
        session.get.side_effect = requests.RequestException("weird")
        with self.assertRaises(IPApiError):
            IPApiClient(session=session).get_ipv4()

    def test_error_keeps_original_cause(self):
        session = MagicMock()
        session.get.side_effect = requests.Timeout("too slow")
        with self.assertRaises(IPApiError) as ctx:
            IPApiClient(session=session).get_ipv4()
        self.assertIsInstance(ctx.exception.__cause__, requests.Timeout)

    def test_error_message_names_the_action(self):
        session = MagicMock()
        session.get.side_effect = requests.Timeout("too slow")
        with self.assertRaisesRegex(IPApiError, "retrieve IPv6"):
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

    def test_location_without_ip_propagates_ipv4_failure(self):
        session = MagicMock()
        session.get.side_effect = requests.ConnectionError("offline")
        with self.assertRaises(IPApiError):
            IPApiClient(session=session).get_location()

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
        with self.assertRaisesRegex(IPApiError, "lookup failed"):
            IPApiClient(session=session).get_location("8.8.8.8")

    def test_non_dict_location_response_raises(self):
        session = fake_session("oops")
        with self.assertRaisesRegex(IPApiError, "invalid JSON response"):
            IPApiClient(session=session).get_location("8.8.8.8")

    def test_invalid_ip_argument_raises_before_request(self):
        session = MagicMock()
        with self.assertRaisesRegex(IPApiError, "Invalid IP address"):
            IPApiClient(session=session).get_location("bad-ip")
        session.get.assert_not_called()

    def test_http_error_on_location_becomes_api_error(self):
        session = fake_session(dict(self.PAYLOAD), error=http_error(429))
        with self.assertRaisesRegex(IPApiError, "HTTP error 429"):
            IPApiClient(session=session).get_location("8.8.8.8")

    def test_timeout_on_location_becomes_api_error(self):
        session = MagicMock()
        session.get.side_effect = requests.Timeout("slow")
        with self.assertRaisesRegex(IPApiError, "look up location"):
            IPApiClient(session=session).get_location("8.8.8.8")


if __name__ == "__main__":
    unittest.main()
