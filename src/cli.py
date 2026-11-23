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

    LABELS = {
        "ip": "IP",
        "isp": "ISP",
        "cidr": "CIDR",
        "ipv4": "IPv4",
        "ipv6": "IPv6",
        "mac": "MAC",
    }

    @classmethod
    def _label(cls, key):
        key = str(key)
        if key.lower() in cls.LABELS:
            return cls.LABELS[key.lower()]
        return key.replace("_", " ").title()

    def _show_fields(self, title, data):
        print(f"\n=== {title} ===")
        for key, value in data.items():
            print(f"{self._label(key)}: {value}")

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
        self._show_fields("IP GEOLOCATION", data)

    def show_subnet(self, data):
        self._show_fields("SUBNET INFORMATION", data)

    def show_local_network(self, data):
        self._show_fields("LOCAL NETWORK", data)

    def show_ports(self, ports):
        print("\n=== OPEN TCP PORTS ===")
        print(f"Total open ports: {len(ports)}")

        for port, service in ports:
            print(f"Port {port}: {service}")

    def show_error(self, error):
        print(f"Error: {error}")

    def show_message(self, message):
        print(message)

    def show_report(self, report):
        print("\n" + "=" * self.WIDTH)
        print("FULL NETWORK REPORT".center(self.WIDTH))
        print("=" * self.WIDTH)

        for key in ("ipv4", "ipv6"):
            if report.get(key) is not None:
                self.show_ip(report[key])

        if report.get("location"):
            self.show_location(report["location"])

        for network in report.get("networks") or []:
            self.show_local_network(network)

        if report.get("ports") is not None:
            self.show_ports(report["ports"])

        for error in report.get("errors") or []:
            self.show_error(error)