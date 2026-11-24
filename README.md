# NetIP-Inspector

A Python command-line application that inspects your network: public IPv4 and IPv6 addresses, IP geolocation, local interfaces (IP and MAC), a subnet calculator, and a local TCP port scanner. It uses REST APIs, JSON and Object-Oriented Programming.

## Features

| Menu option | What it does |
|---|---|
| 1. Display IPv4 address | Shows your public IPv4 address |
| 2. Display IPv6 address | Shows your public IPv6 address |
| 3. Display both addresses | Shows IPv4 and IPv6 together |
| 4. Display IP geolocation | Country, region, city, coordinates and ISP of an IP |
| 5. Display local IP and MAC | Lists local network interfaces with IPv4, subnet mask and MAC |
| 6. Subnet calculator | Network, broadcast, masks, host range and host count (IPv4) |
| 7. Scan local TCP ports | Finds open TCP ports on this computer |
| 8. Full network report | Combines the results above in one report |
| 0. Exit | Quits the application |

## Requirements

- Python 3.7 or newer
- Internet access for options 1 to 4 (options 5 to 7 work offline)
- The packages in `requirements.txt`: `requests` and `psutil`

## Installation

```bash
git clone https://github.com/azzouzlouay0/NetIP-Inspector.git
cd NetIP-Inspector
pip install -r requirements.txt
```

## Running

```bash
python -m src.main
```

On Windows, if `python` is not recognized, use `py -m src.main` instead.

## Project structure

```
NetIP-Inspector/
├── src/
│   ├── __init__.py
│   ├── cli.py              # menu and all screen output
│   ├── ip_address_info.py  # IP parsing and subnet calculations
│   ├── ip_api_client.py    # REST API client (public IP, geolocation)
│   ├── network_info.py     # local interfaces, IPv4, subnet mask, MAC
│   └── port_scanner.py     # TCP port scanner
├── tests/                  # automated unit tests
├── docs/                   # detailed documentation
├── requirements.txt
└── README.md
```

## Documentation

- [Usage guide](docs/usage.md): every menu option with example output
- [Architecture](docs/architecture.md): modules, classes and data flow
- [Testing](docs/testing.md): how to run the tests and what they cover
- [Demo guide](docs/demo.md): step-by-step script for the final presentation

## Running the tests

```bash
python -m unittest discover -s . -p "test_*.py"
```

The tests need no internet connection. See [docs/testing.md](docs/testing.md) for details.

## Team

| Member | Role |
|---|---|
| Louay | Scrum Leader, DevOps, integration |
| Adem | Backend, REST API developer |
| Saddem | CLI developer, QA, documentation |

## Technologies

Python 3, REST APIs (ipify, ipwho.is), JSON, Git and GitHub, Object-Oriented Programming, `unittest`.
