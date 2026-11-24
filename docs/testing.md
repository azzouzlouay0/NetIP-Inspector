# Testing

The project has 76 automated unit tests in the `tests/` folder, written with Python's built-in `unittest`. They need no internet connection.

## Requirements

Install the dependencies once (`psutil` is needed by the `network_info` tests):

```bash
pip install -r requirements.txt
```

## Running the tests

### Command line

From the project's root folder:

```bash
python -m unittest discover -s . -p "test_*.py"
```

On Windows, use `py` instead of `python` if `python` is not recognized. If you use `pytest`, `python -m pytest tests` also works.

### VS Code

1. Open the **Testing** panel (flask icon in the left bar).
2. Click **Configure Python Tests**, then choose **unittest**, the folder **tests**, and the pattern `test_*.py`.
3. Click **Run All Tests**. Every test should show a green check.

A successful run ends with `OK`. VS Code's Testing panel also counts subtests (checks repeated over several values), so it shows a higher total, 88, than the 76 tests reported by `unittest`.

## What is covered

| File | Tests | What it checks |
|---|---|---|
| `test_ip_address_info.py` | 13 | IPv4 and IPv6 parsing, normalization, invalid input, subnet calculations for `/0`, `/16`, `/24`, `/30`, `/31`, `/32`, invalid prefixes, IPv6 rejection |
| `test_ip_api_client.py` | 27 | Public IP and geolocation parsing, wrong IP version, missing or invalid data, and every failure (timeout, connection, HTTP status, invalid JSON) turning into `IPApiError` |
| `test_cli.py` | 21 | Menu content and centering, the user's input handling, every display method, acronym labels, the full report |
| `test_network_info.py` | 6 | Interfaces with and without IPv4 or MAC, several interfaces, no interfaces, one real call |
| `test_port_scanner.py` | 9 | Port range validation, open and closed ports, scanning ranges |

## How the tests avoid the internet

- **API client:** the HTTP session is replaced by a fake object (`unittest.mock`) that returns prepared answers or raises errors such as `requests.Timeout`.
- **Network info:** `psutil.net_if_addrs` is replaced by fake interface data, so the result does not depend on the computer running the tests.
- **Port scanner:** the tests open their own server on `127.0.0.1` with a free port chosen by the system, and use a port that is guaranteed closed.
- **CLI:** `input()` is replaced by a fake answer and the printed text is captured and compared.

## Adding a test

1. Add a method starting with `test_` to the matching class, or create `tests/test_<module>.py`.
2. Import the class with `from src.<module> import <Class>`.
3. Run the whole suite and make sure it still ends with `OK`.

## Known limits

- The real online services (ipify, ipwho.is) are not called by the tests. Their real answers are checked by running the application.
- The port scanner tests use only `127.0.0.1`.
