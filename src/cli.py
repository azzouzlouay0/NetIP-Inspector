class CLI:
    WIDTH = 40

    OPTIONS = [
        "1. Display IPv4 address",
        "2. Display IPv6 address",
        "3. Display both addresses",
        "4. Display IP geolocation",
        "5. Display local IP and MAC",
        "6. Subnet calculator",
        "7. Scan local TCP ports",
        "8. Full network report",
        "0. Exit",
    ]

    def _build_menu(self):
        line = "=" * self.WIDTH

        lines = [
            line,
            "NETIP-INSPECTOR".center(self.WIDTH),
            line,
            ""
        ]

        lines += [
            option.center(self.WIDTH)
            for option in self.OPTIONS
        ]

        lines += ["", line]
        return "\n".join(lines)

    def ask_choice(self):
        print()
        print(self._build_menu())
        return input("Enter your choice: ").strip()

    def show_ip(self, info):
        print(
            f"IPv{info.version} public address: "
            f"{info.address}"
        )

    def show_location(self, data):
        print("\n=== IP GEOLOCATION ===")
        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def show_subnet(self, data):
        print("\n=== SUBNET INFORMATION ===")

        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def show_local_network(self, data):
        print("\n=== LOCAL NETWORK ===")

        for key, value in data.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

    def show_ports(self, ports):
        print("\n=== OPEN TCP PORTS ===")
        print(f"Total open ports: {len(ports)}")

        for port, service in ports:
            print(f"Port {port}: {service}")

    def show_error(self, error):
        print(f"Error: {error}")

    def show_message(self, message):
        print(message)
