import socket
from concurrent.futures import ThreadPoolExecutor


class PortScanner:

    def __init__(self, host="127.0.0.1"):
        self.host = host

    def check_port(self, port):
        with socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        ) as sock:

            sock.settimeout(0.3)
            result = sock.connect_ex((self.host, port))

            if result == 0:
                try:
                    service = socket.getservbyport(
                        port, "tcp"
                    )
                except OSError:
                    service = "Unknown"

                return port, service

        return None

    def scan(self, start=1, end=1024):
        if not (1 <= start <= end <= 65535):
            raise ValueError("Invalid port range")

        with ThreadPoolExecutor(max_workers=32) as executor:
            results = executor.map(
                self.check_port,
                range(start, end + 1)
            )

            return [
                result for result in results
                if result is not None
            ]
