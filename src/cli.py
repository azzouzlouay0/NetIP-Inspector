class CLI:
    WIDTH = 32

    OPTIONS = [
        "1. Display IPv4 address",
        "2. Display IPv6 address",
        "3. Display both addresses",
        "0. Exit",
    ]

    def _build_menu(self):
        line = "=" * self.WIDTH
        lines = [line, "NETIP-INSPECTOR".center(self.WIDTH), line, ""]
        lines += [option.center(self.WIDTH) for option in self.OPTIONS]
        lines += ["", line]
        return "\n".join(lines)

    def ask_choice(self):
        print()
        print(self._build_menu())
        prompt = "Enter your choice: "
        margin = " " * ((self.WIDTH - len(prompt)) // 2)
        return input(margin + prompt).strip()

    def show_ip(self, info):
        print(f"IPv{info.version} public address: {info.address}")

    def show_error(self, error):
        print(f"Error: {error}")

    def show_message(self, message):
        print(message)