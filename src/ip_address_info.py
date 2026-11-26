from dataclasses import dataclass
from ipaddress import ip_address, ip_interface


@dataclass(frozen=True)
class IPAddressInfo:
    address: str

    def __post_init__(self):
        parsed = ip_address(self.address)
        object.__setattr__(self, "address", str(parsed))

    @property
    def version(self):
        return ip_address(self.address).version

    @property
    def is_global(self):
        return ip_address(self.address).is_global

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
