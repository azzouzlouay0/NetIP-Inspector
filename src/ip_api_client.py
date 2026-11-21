import requests

from .ip_address_info import IPAddressInfo


class IPApiClient:
    IPV4_URL = "https://api4.ipify.org?format=json"
    IPV6_URL = "https://api6.ipify.org?format=json"
    LOCATION_URL = "https://ipwho.is/"

    def __init__(self, timeout=5.0, session=None):
        self._timeout = timeout
        self._session = (
            session if session is not None
            else requests.Session()
        )

    def _fetch(self, url):
        response = self._session.get(
            url, timeout=self._timeout
        )
        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, dict) or "ip" not in payload:
            raise ValueError("Invalid IP API response")

        return IPAddressInfo(payload["ip"])

    def get_ipv4(self):
        return self._fetch(self.IPV4_URL)

    def get_ipv6(self):
        return self._fetch(self.IPV6_URL)

    def get_location(self, ip=None):
        if ip is None:
            ip = self.get_ipv4().address

        parsed = IPAddressInfo(ip)
        url = self.LOCATION_URL + parsed.address

        response = self._session.get(
            url, timeout=self._timeout
        )
        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict) or not data.get("success"):
            raise ValueError("Geolocation lookup failed")

        connection = data.get("connection") or {}

        return {
            "ip": data.get("ip", parsed.address),
            "country": data.get("country", "Unknown"),
            "region": data.get("region", "Unknown"),
            "city": data.get("city", "Unknown"),
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "isp": connection.get("isp", "Unknown")
        }
