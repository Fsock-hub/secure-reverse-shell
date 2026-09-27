## Reverse Shell

Reverse Shell v0.4 — a lightweight and robust reverse shell implemented in pure Python using the standard socket and subprocess libraries. The project was built from scratch for educational purposes to understand network programming, custom socket protocols, and system administration.
Features

- Reverse Connection Architecture: The client initiates the connection to the server, allowing it to bypass standard firewalls and NAT configurations.

- Persistent Reconnection Loop: If the server is offline or restarts, the client handles the exception and automatically retries the connection every 10 seconds       without crashing.

- Custom 64-bit Header Protocol: Solves the classic "socket freeze" issue. The client calculates the precise data size and sends a fixed-length header first. The      server reads exactly that amount of bytes, preventing hangs on empty command outputs (e.g., color 2).

- Directory Navigation: Embedded interceptor for the cd command using Python's os module. Allows seamless folder switching across the remote filesystem.

- Cross-Platform Readiness: Designed to be easily compiled into a stealthy, background executable using PyInstaller.

## Installation & Usage
  Prerequisites

    Python 3.x installed on both machines (only required for running raw scripts).

## Quick Start

    Start the server on your control machine:
    ```bash

    python server.py
    ```
## Launch the client on the managed system:
    ```bash

    python client.py
    ```
## TODO

    - AES encryption for traffic.

    - File upload and download using chunks.

- Disclaimer

This project is created strictly for educational purposes, authorized security auditing, and internal penetration testing. Do not run this software on devices you do not own or do not have explicit permission to test. The author is not responsible for any misuse or damage caused by this program.
