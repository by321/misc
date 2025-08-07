import socket, threading, sys, getopt, platform, struct

"""
Simple TCP chat server and client program.
Usage:
  python chat.py [-n name] [-p port] [-c server_ip]
    -n <name>: Specify server name (default: host computer name)
    -p <port>: Specify port number (default: 12345)
    -c <server_ip>: Connect to server at specified IP address
  Will run as server without the "-c" option.
  To run as client, use the "-c" option to specify server IP address.
  Type messages and press ENTER to send, press Ctrl-C to exit.
"""

def get_hostname():
    return platform.node()

def send_all(sock, data):
    while data:
        sent = sock.send(data)
        data = data[sent:]

def receive_one_message(sock):
    raw_length = b""
    while len(raw_length) < 4:
        data = sock.recv(4 - len(raw_length))
        if not data:
            return None
        raw_length += data
    length = struct.unpack('<I', raw_length)[0]

    received = b""
    while len(received) < length:
        data = sock.recv(min(length - len(received), 1024))
        if not data:
            return None
        received += data
    return received

def receive_messages(sock, remote_name):
    while True:
        data = receive_one_message(sock)
        if data is None:
            break
        print('\n'+remote_name + ": " + data.decode())

def input_and_send_loop(sock):
    while True:
        try:
            message = input()
            msg_data = message.encode()
            send_all(sock, struct.pack('<I', len(msg_data)) + msg_data)
        except:
            break


def server_loop(sock, name):
    ip_address = socket.gethostbyname(socket.gethostname())
    print(f"Starting server, ip={ip_address}, name={name}")
    print("press Ctrl-Break to exit")

    while True:
        client_sock, addr = sock.accept()
        client_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        print(f"Connected to client at {addr}")
        message = f"{name}: Connected".encode()
        send_all(client_sock, struct.pack('<I', len(message)) + message)

        data = receive_one_message(client_sock)
        if data is None:
            client_sock.close()
            continue
        client_name = data.decode().split(":")[0]
        print(data.decode())

        threading.Thread(target=receive_messages, args=(client_sock, client_name), daemon=True).start()
        input_and_send_loop(client_sock)

        client_sock.close()
        break
    sock.close()

def client_loop(sock, server_addr, name):
    print(f"Connecting to server at {server_addr} as '{name}'")
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.connect(server_addr)
        message = f"{name}: Connected".encode()
        send_all(sock, struct.pack('<I', len(message)) + message)

        data = receive_one_message(sock)
        if data is None:
            sock.close()
            return
        server_name = data.decode().split(":")[0]
        print(data.decode())

        threading.Thread(target=receive_messages, args=(sock, server_name), daemon=True).start()
        input_and_send_loop(sock)

    except Exception as e:
        print(f"Connection failed: {e}")
    finally:
        sock.close()

def main():
    name = get_hostname()
    is_client = False
    server_ip = None
    port = 12345  # Default port

    try:
        opts, _ = getopt.getopt(sys.argv[1:], "c:n:p:")
        for opt, arg in opts:
            if opt == '-c':
                is_client = True
                server_ip = arg
            elif opt == '-n':
                name = arg
            elif opt == '-p':
                try:
                    port = int(arg)
                    if not 1 <= port <= 65535:
                        raise ValueError("Port must be between 1 and 65535")
                except ValueError as e:
                    print(f"Invalid port: {e}")
                    sys.exit(1)
    except getopt.GetoptError:
        print("Usage: python chat.py [-c <server_ip>] [-n <name>] [-p <port>]")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if is_client:
        if not server_ip:
            print("Client mode requires server IP (-c)")
            sys.exit(1)
        client_loop(sock, (server_ip, port), name)
    else:
        sock.bind(('0.0.0.0', port))
        sock.listen(1)
        server_loop(sock, name)

if __name__ == "__main__":
    main()