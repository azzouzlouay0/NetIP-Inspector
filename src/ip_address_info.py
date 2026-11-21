from ipaddress import ip_address, ip_interface


class IPAddressInfo:
    def __init__(self, address):
        parsed = ip_address(address)
        self.address = str(parsed)
        self.version = parsed.version

    def __str__(self):
        return f"IPv{self.version}: {self.address}"

    def subnet_details(self, prefix):
        interface = ip_interface(f"{self.address}/{prefix}")
        network = interface.network

        if self.version != 4:
            raise ValueError("Subnet calculator supports IPv4 only")

        wildcard = ".".join(
            str(255 - int(octet))
            for octet in str(network.netmask).split(".")
        )

        if network.prefixlen == 32:
            first = last = str(network.network_address)
            host_count = 1
        elif network.prefixlen == 31:
            first = str(network.network_address)
            last = str(network.broadcast_address)
            host_count = 2
        else:
            first = str(network.network_address + 1)
            last = str(network.broadcast_address - 1)
            host_count = network.num_addresses - 2

        return {
            "ip": self.address,
            "cidr": str(network),
            "subnet_mask": str(network.netmask),
            "wildcard_mask": wildcard,
            "network": str(network.network_address),
            "broadcast": str(network.broadcast_address),
            "first_host": first,
            "last_host": last,
            "host_count": host_count
        }
