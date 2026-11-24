# Demo guide

A step-by-step script for presenting NetIP-Inspector. A full run takes about five minutes.

## Before the demo

- [ ] Python and the dependencies are installed (`pip install -r requirements.txt`)
- [ ] You are on the `main` branch with the latest code (`git pull origin main`)
- [ ] The terminal is open in the project folder with a large font
- [ ] The tests pass (see the tests step below)
- [ ] You know whether the network provides IPv6 (option 2 shows an error if not, which is useful for the demo)

## 1. Introduce the project (30 seconds)

NetIP-Inspector is a Python command-line tool for inspecting a network. It has three parts: the REST API client (Adem), the application and integration (Louay), and the CLI, tests and documentation (Saddem).

## 2. Start the application

```bash
python -m src.main
```

Show the centered menu. Point out that it has 8 functions and an exit option.

## 3. Walk through the options

| Step | Type | What to show and say |
|---|---|---|
| 1 | `1` | Your public IPv4 address, obtained from a REST API |
| 2 | `2` | Your public IPv6 address. If the network has none, show the `Error:` line and explain that the application handles failures without crashing |
| 3 | `3` | Both addresses together |
| 4 | `4` | Geolocation: country, city and ISP. Mention that it is approximate |
| 5 | `5` | Local interfaces with IPv4, subnet mask and MAC address |
| 6 | `6` | Subnet calculator, for example `192.168.1.10` with prefix `24`. Point out the network, broadcast, wildcard mask and 254 hosts |
| 7 | `7` | Scan of the local TCP ports (default range 1 to 1024) with service names |
| 8 | `8` | The full report that combines everything |
| 9 | `0` | Exit |

## 4. Show error handling (optional, 1 minute)

Disconnect from the network (or turn off Wi-Fi) and choose option `1`. The error is printed on one clear line, for example `Error: Unable to retrieve IPv4: network connection failed`. Options 5, 6 and 7 still work, because they do not need the internet.

## 5. Show the tests (1 minute)

```bash
python -m unittest discover -s . -p "test_*.py"
```

Explain that there are 76 tests, that they run in under a second, and that they do not need the internet because the API is replaced by a fake. The run should end with `OK`.

## 6. Show the team workflow (optional)

On GitHub, open the **Pull requests** tab and the **Closed** list. Each task was developed on its own branch (for example `feature/SAD-05-tests`), reviewed by the Scrum Leader, and merged into `main`.

## If something goes wrong

| Problem | What to do |
|---|---|
| `python` is not recognized | Use `py -m src.main` on Windows |
| `No module named 'requests'` or `'psutil'` | Run `pip install -r requirements.txt` |
| No internet during the demo | Use options 5, 6 and 7, and show the error message for options 1 to 4 as an error-handling example |
| Option 2 shows an error | Normal on a network without IPv6. Explain it, then continue |
| Option 7 is slow | Wait up to about ten seconds: 1024 ports are being checked |

## Questions you may be asked

- **Why is only the CLI class printing?** So the logic can change or be tested without touching the display.
- **How do you test the API without the internet?** The HTTP session is injected into `IPApiClient`, so tests give it a fake session.
- **Why one error type?** The application only has to catch `IPApiError`, whatever went wrong with the service.
- **Is the geolocation exact?** No. It usually shows the provider's location, not the device's.
