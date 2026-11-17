from ipaddress import ip_address


class IPAddressInfo:

    def __init__(self, address):
        parsed = ip_address(address)
        self.address = str(parsed)
        self.version = parsed.version

    def __str__(self):
        return f"IPv{self.version}: {self.address}"
