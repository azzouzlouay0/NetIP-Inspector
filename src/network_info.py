import socket
import psutil


class NetworkInfo:

    def get_network_details(self):
        results = []

        interfaces = psutil.net_if_addrs()

        for name, addresses in interfaces.items():
            info = {"interface": name}

            for addr in addresses:
                if addr.family == socket.AF_INET:
                    info["ipv4"] = addr.address
                    info["subnet_mask"] = addr.netmask

                elif addr.family in (
                    getattr(psutil, "AF_LINK", None),
                    getattr(socket, "AF_PACKET", None),
                ):
                    info["mac"] = addr.address

            if "ipv4" in info:
                results.append(info)

        return results
