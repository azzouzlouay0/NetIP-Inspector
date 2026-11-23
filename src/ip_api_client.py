import requests

from .ip_address_info import IPAddressInfo


class IPApiError(Exception):
    """Raised when the public IP API cannot return a valid answer."""


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

    def _get_json(self, url, action):
        """GET a URL and return its JSON dict, or raise IPApiError."""
        try:
            response = self._session.get(url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.Timeout as exc:
            raise IPApiError(f"Unable to {action}: request timed out") from exc
        except requests.ConnectionError as exc:
            raise IPApiError(
                f"Unable to {action}: network connection failed"
            ) from exc
        except requests.HTTPError as exc:
            raise IPApiError(
                f"Unable to {action}: HTTP error {exc.response.status_code}"
            ) from exc
        except (requests.RequestException, ValueError) as exc:
            raise IPApiError(
                f"Unable to {action}: invalid response ({exc})"
            ) from exc

        if not isinstance(payload, dict):
            raise IPApiError(f"Unable to {action}: invalid JSON response")
        return payload

    def _fetch(self, url, expected_version):
        action = f"retrieve IPv{expected_version}"
        payload = self._get_json(url, action)

        raw_ip = payload.get("ip")
        if not isinstance(raw_ip, str):
            raise IPApiError(f"Unable to {action}: missing IP address")

        try:
            info = IPAddressInfo(raw_ip)
        except ValueError as exc:
            raise IPApiError(f"Unable to {action}: invalid IP address") from exc

        if info.version != expected_version:
            raise IPApiError(f"Unable to {action}: incorrect IP version")

        return info

    def get_ipv4(self):
        return self._fetch(self.IPV4_URL, 4)

    def get_ipv6(self):
        return self._fetch(self.IPV6_URL, 6)

    def get_location(self, ip=None):
        if ip is None:
            ip = self.get_ipv4().address

        try:
            parsed = IPAddressInfo(ip)
        except ValueError as exc:
            raise IPApiError(f"Invalid IP address: {ip!r}") from exc

        data = self._get_json(
            self.LOCATION_URL + parsed.address, "look up location"
        )

        if not data.get("success"):
            raise IPApiError("Unable to look up location: lookup failed")

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
