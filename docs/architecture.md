# Architecture

NetIP-Inspector is split into small classes. Each class has one job, and only the `CLI` class prints to the screen. This keeps the logic easy to test and lets the modules be developed independently.

## Modules

| File | Class | Responsibility |
|---|---|---|
| `src/cli.py` | `CLI` | Builds the menu, reads the user's choice and prints every result and error |
| `src/ip_address_info.py` | `IPAddressInfo` | Validates an IP address, stores its version, and calculates IPv4 subnet details |
| `src/ip_api_client.py` | `IPApiClient`, `IPApiError` | Calls the public REST APIs and converts every failure into `IPApiError` |
| `src/network_info.py` | `NetworkInfo` | Reads the local network interfaces with `psutil` |
| `src/port_scanner.py` | `PortScanner` | Scans TCP ports with a thread pool |

## Data flow

```
                +-----------+
   user ------> |    CLI    | <------ prints results and errors
                +-----------+
                      |
        the application calls the modules below
                      |
   +------------------+-------------------+------------------+
   |                  |                   |                  |
IPApiClient      IPAddressInfo       NetworkInfo        PortScanner
   |                  ^                   |                  |
   | creates          | validates         | psutil           | sockets
   +------------------+                   |                  |
   |                                  local interfaces   127.0.0.1
 REST APIs
 ipify, ipwho.is
```

`IPApiClient` returns `IPAddressInfo` objects for public addresses, so every address that enters the application has already been validated.

## Class details

### `CLI`

- `ask_choice()` prints the centered menu and returns the user's choice as a stripped string.
- `show_ip(info)`, `show_location(data)`, `show_subnet(data)`, `show_local_network(data)`, `show_ports(ports)` print one kind of result.
- `show_report(report)` prints the full report from a dictionary with the keys `ipv4`, `ipv6`, `location`, `networks`, `ports` and `errors`. Missing keys are skipped.
- `show_error(error)` and `show_message(message)` print errors and plain messages.
- Field names such as `isp` or `cidr` are printed as `ISP` and `CIDR` through a label table.
- `show_local_network` takes **one** interface dictionary. Loop over the list returned by `NetworkInfo`.

### `IPAddressInfo`

- `IPAddressInfo("192.168.1.10")` stores `address` (normalized) and `version` (4 or 6). An invalid address raises `ValueError`.
- `subnet_details(prefix)` returns a dictionary with the CIDR, subnet mask, wildcard mask, network, broadcast, first and last host, and host count. It handles `/31` and `/32` specially and raises `ValueError` for IPv6 or an invalid prefix.

### `IPApiClient` and `IPApiError`

- `get_ipv4()` and `get_ipv6()` return an `IPAddressInfo`.
- `get_location(ip=None)` returns a dictionary with `ip`, `country`, `region`, `city`, `latitude`, `longitude` and `isp`. Without an argument it uses the caller's public IPv4 address.
- Timeouts, connection errors, HTTP errors, invalid JSON, a missing or invalid IP, and a wrong IP version are all raised as `IPApiError` with a readable message. The original exception is kept as the cause.
- The HTTP session is passed in through the constructor (`session=`), so tests can replace it with a fake and never touch the network.

### `NetworkInfo`

- `get_network_details()` returns a list of dictionaries, one per interface that has an IPv4 address, with `interface`, `ipv4`, `subnet_mask` and, when available, `mac`.

### `PortScanner`

- `PortScanner(host="127.0.0.1")`.
- `check_port(port)` returns `(port, service)` if the port is open, otherwise `None`. The service name is `Unknown` when the port has no registered name.
- `scan(start=1, end=1024)` checks the range with 32 threads and returns the open ports. It raises `ValueError` unless `1 <= start <= end <= 65535`.

## Design decisions

- **One class, one job.** Only `CLI` prints. The other classes return data, so the CLI can be changed without touching the logic.
- **One error type for the online services.** The application catches `IPApiError` instead of many `requests` exceptions.
- **Validation at the entrance.** An address becomes an `IPAddressInfo` before anything else uses it.
- **Testable by design.** The API client takes an injectable session, and the scanner and network reader are tested without real internet access (see [testing.md](testing.md)).

## External services

| Service | Used for |
|---|---|
| `api4.ipify.org` | Public IPv4 address |
| `api6.ipify.org` | Public IPv6 address |
| `ipwho.is` | IP geolocation |

All requests use a 5-second timeout by default.
