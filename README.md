# Reverse-Shell
# Reverse-shell  - Version 0.4

A lightweight, robust **Reverse Shell** implemented in clean Python using the standard `socket` and `subprocess` libraries. This project was developed from scratch for educational purposes to understand network programming, custom socket protocols, and systems administration.

##  Features

* **Reverse Connection Architecture:** The client initiates the connection to the server, allowing it to bypass standard firewalls and NAT configurations.
* **Persistent Reconnection Loop:** If the server is offline or restarts, the client handles the exception and automatically retries the connection every 10 seconds without crashing.
* **Custom 64-bit Header Protocol:** Solves the classic "socket freeze" issue. The client calculates the precise data size and sends a fixed-length header first. The server reads exactly that amount of bytes, preventing hangs on empty command outputs (e.g., `color 2`).
* **Active Directory Navigation:** Embedded interceptor for the `cd` command utilizing Python's `os` module. Allows seamless folder switching across the remote filesystem.
* **Cross-Platform Readiness:** Designed to be easily compiled into a stealthy, background executable using PyInstaller.

##  Installation & Usage

### Prerequisites
* Python 3.x installed on both target machines (only required for running raw scripts).

### Quick Start
1. **Start the Server:** Run the listener on your control machine first:
   ```bash
   python server.py
   ```
2. **Launch the Client:** Run the client on the managed system:
   ```bash
   python client.py
   ```
## TO DO

`AES Encryption`
Upload, download files using `chunks`

##  Disclaimer

This project is created strictly for **educational purposes**, authorized security auditing, and internal penetration testing. Do not run this software on devices you do not own or do not have explicit permission to test. The author is not responsible for any misuse or damage caused by this program.
