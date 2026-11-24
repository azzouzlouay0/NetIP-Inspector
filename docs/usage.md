# Usage guide

Start the application and type the number of an option, then press Enter.

```
========================================
            NETIP-INSPECTOR
========================================

        1. Display IPv4 address
        2. Display IPv6 address
       3. Display both addresses
       4. Display IP geolocation
      5. Display local IP and MAC
          6. Subnet calculator
        7. Scan local TCP ports
         8. Full network report
                0. Exit

========================================
Enter your choice:
```

The examples below use documentation-reserved addresses (such as `203.0.113.25`). Your own output will show your real values.

## 1, 2 and 3: Public IP address

Option 1 shows your public IPv4 address, option 2 your public IPv6 address, and option 3 both. The addresses come from the ipify service.

```
IPv4 public address: 203.0.113.25
IPv6 public address: 2001:db8::25
```

Many home and mobile networks have no IPv6. In that case option 2 shows an error message instead of an address (see [Error messages](#error-messages)). This is expected.

## 4: IP geolocation

Shows where an IP address is located and which provider owns it, using the ipwho.is service. The lookup uses your own public IPv4 address unless another address is given. Fields the service does not return are shown as `Unknown`.

```
=== IP GEOLOCATION ===
IP: 203.0.113.25
Country: Tunisia
Region: Bizerte
City: Bizerte
Latitude: 37.27
Longitude: 9.87
ISP: Example Telecom
```

Geolocation is approximate. It usually points to the provider's location, not the exact position of the device.

## 5: Local IP and MAC

Lists each network interface of this computer that has an IPv4 address, with its subnet mask and MAC address. Nothing is sent over the internet.

```
=== LOCAL NETWORK ===
Interface: Wi-Fi
IPv4: 192.168.1.23
Subnet Mask: 255.255.255.0
MAC: AA-BB-CC-DD-EE-FF
```

One block is shown per interface.

## 6: Subnet calculator

Calculates the details of an IPv4 address with a prefix length (CIDR), for example `192.168.1.10/24`. IPv6 addresses are not supported by this option.

```
=== SUBNET INFORMATION ===
IP: 192.168.1.10
CIDR: 192.168.1.0/24
Subnet Mask: 255.255.255.0
Wildcard Mask: 0.0.0.255
Network: 192.168.1.0
Broadcast: 192.168.1.255
First Host: 192.168.1.1
Last Host: 192.168.1.254
Host Count: 254
```

Special cases: a `/31` network has 2 usable hosts and a `/32` has exactly 1. A prefix outside 0 to 32 is rejected with an error message.

## 7: Scan local TCP ports

Checks which TCP ports are open on this computer (`127.0.0.1`). The scanner's default range is ports 1 to 1024, waits 0.3 seconds per port, and tests 32 ports at the same time. The service name is shown when it is known, otherwise `Unknown`.

```
=== OPEN TCP PORTS ===
Total open ports: 2
Port 135: epmap
Port 445: microsoft-ds
```

The result depends on the programs running on your computer. `Total open ports: 0` means nothing is listening in that range.

## 8: Full network report

Combines the results of the other options into one report. The screen prints each part that is available and lists any errors at the end of the report (for example the IPv6 lookup on a network without IPv6).

```
========================================
          FULL NETWORK REPORT
========================================
IPv4 public address: 203.0.113.25

=== IP GEOLOCATION ===
...

=== LOCAL NETWORK ===
...

=== OPEN TCP PORTS ===
...
Error: Unable to retrieve IPv6: network connection failed
```

## 0: Exit

Quits the application.

## Error messages

Errors are printed on one line, starting with `Error:`.

| Message | Meaning |
|---|---|
| `Unable to ...: request timed out` | The online service did not answer in 5 seconds |
| `Unable to ...: network connection failed` | No internet connection, or no IPv6 on this network |
| `Unable to ...: HTTP error 429` | The service refused the request (here 429, too many requests) |
| `Unable to ...: invalid response (...)` | The service answered with data that is not valid JSON |
| `Unable to ...: invalid JSON response` | The answer was JSON but not in the expected form |
| `Unable to ...: missing IP address` | The answer did not contain an IP address |
| `Unable to ...: invalid IP address` | The address in the answer is not a valid IP |
| `Unable to ...: incorrect IP version` | An IPv6 address came back where IPv4 was expected, or the reverse |
| `Unable to look up location: lookup failed` | The geolocation service could not locate the address |
| `Invalid IP address: '...'` | The address you entered is not a valid IP |
| `Subnet calculator supports IPv4 only` | An IPv6 address was given to option 6 |
| `Invalid port range` | The start and end ports are not between 1 and 65535, or are in the wrong order |
