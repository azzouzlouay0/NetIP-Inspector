import requests

from .ip_address_info import IPAddressInfo


class IPApiClient:

    IPV4_URL = "https://api4.ipify.org?format=json"
    IPV6_URL = "https://api6.ipify.org?format=json"

    def __init__(self, timeout=5.0, session=None):
        self._timeout = timeout
        self._session = session if session is not None else requests.Session()

    def _fetch(self, url):
        response = self._session.get(url, timeout=self._timeout)
        payload = response.json()
        return IPAddressInfo(payload["ip"])

    def get_ipv4(self):
        return self._fetch(self.IPV4_URL)

    def get_ipv6(self):
        return self._fetch(self.IPV6_URL)
