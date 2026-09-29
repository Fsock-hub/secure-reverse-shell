
# Secure Reverse Shell

A lightweight, encrypted reverse shell implemented in pure Python using the standard `socket`, `subprocess`, and `cryptography` libraries. The project was built from scratch for educational purposes to understand network programming, custom socket protocols, symmetric encryption, and secure key exchange.

## Features

- **Reverse Connection Architecture:** The client initiates the connection to the server, allowing it to bypass standard firewalls and NAT configurations.
- **Persistent Reconnection Loop:** If the server is offline or restarts, the client handles the exception and automatically retries the connection every 10 seconds without crashing.
- **Custom 64-bit Header Protocol:** Solves the classic "socket freeze" issue. The client calculates the precise data size and sends a fixed-length header first. The server reads exactly that amount of bytes, preventing hangs on empty command outputs.
- **Automatic Key Exchange:** On first launch, if the client does not have a key, it requests one from the server. The server generates a symmetric key (Fernet) and sends it to the client. The client saves it and uses it for all subsequent communication.
- **AES Encryption:** All commands and output are encrypted using the Fernet symmetric encryption scheme (AES-128 in CBC mode with HMAC-SHA256 for authentication).
- **Directory Navigation:** Embedded interceptor for the `cd` command using Python's `os` module. Allows seamless folder switching across the remote filesystem.
- **Cross-Platform Readiness:** Designed to be easily compiled into a stealthy, background executable using PyInstaller.

## How It Works

### 1. Key Generation and Storage

- On the server side, a symmetric key is generated on the first launch and stored in `secret.key`.
- The key is a URL-safe base64-encoded 32-byte key, as required by the `cryptography.fernet` module.
- The client also stores the key in `secret.key`. If the file does not exist, it requests the key from the server.

### 2. Key Exchange Protocol

- When the client starts and does not have a key, it connects to the server and sends the command `REQUEST_KEY`.
- The server receives this command, reads its own `secret.key`, and sends it to the client.
- The client saves the key locally and sends `KEY_RECEIVED` as confirmation.
- The server closes the connection. The client then reconnects to the server for normal operation and sends `HELLO` to indicate that it is ready.
- If the client already has a key, it skips the key exchange and sends `HELLO` immediately after connecting.

### 3. Encrypted Communication

- After the handshake, the server prompts the user for a command.
- The command is encrypted using the Fernet key and sent to the client.
- The client decrypts the command, executes it via `subprocess`, encrypts the output, and sends it back to the server.
- The server decrypts the output and displays it.
- All data transmitted over the network is encrypted and unreadable without the key.

### 4. Protocol Details

- **Header:** Each message starts with a 64-byte header containing the length of the encrypted payload. This is sent in plaintext to allow the receiver to know how many bytes to read.
- **Acknowledgment:** After receiving the header, the receiver sends `OK_SIZE` to confirm. The sender then transmits the encrypted payload.
- **Payload:** The encrypted data, which is decrypted on the receiving end using the shared key.

## Installation & Usage

### Prerequisites

- Python 3.10 or higher on both machines.
- `cryptography` library installed (`pip install cryptography`).

### Quick Start

1. Start the server on your control machine:
   ```bash
   python server.py
   ```
2. Launch the client on the managed system:
   ```bash
   python client.py
   ```
3. On first run, the client will automatically request the key from the server. If the server is not running, the client will retry every 10 seconds.

## TODO

- File upload and download using chunks.
- Asymmetric encryption for key exchange (RSA) to avoid sending the key in plaintext.
- Obfuscation of the key path and server address.

## Disclaimer

This project is created strictly for educational purposes, authorized security auditing, and internal penetration testing. Do not run this software on devices you do not own or do not have explicit permission to test. The author is not responsible for any misuse or damage caused by this program.
