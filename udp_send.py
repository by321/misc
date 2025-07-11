import sys, time, socket

def send_udp_packet(message, host, port, repeat=1, delay_ms=0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        for i in range(repeat):
            sock.sendto(message.encode(), (host, port))
            print(f"Sent '{message}' to {host}:{port} (iteration {i+1}/{repeat})")
            if i < repeat - 1 and delay_ms > 0:
                time.sleep(delay_ms / 1000.0)
    except Exception as e:
        print(f"Error sending UDP packet: {e}")
    finally:
        sock.close()

def main():
    if len(sys.argv)!=4 and len(sys.argv)!=6:
        print("usage: python udp_send.py <host> <port> <message> [<repeat> <delay_ms>]")
        print("example: python udp_send.py 192.168.1.100 12345 start")
        print("example: python udp_send.py 192.168.1.100 12345 start 5 100")
        sys.exit(1)
    
    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except ValueError:
        print(f"invalid port specified: {sys.argv[2]}")
    
    message = sys.argv[3]
    repeat = 1 ; delay_ms = 0 # check for -m flag
    if len(sys.argv)==6:
        try:
            repeat = int(sys.argv[4])
            delay_ms = int(sys.argv[5])
            if repeat < 1:
                sys.exit("error: repeat count must be at least 1")
            if delay_ms < 0:
                sys.exit("error: delay must be non-negative")
        except ValueError:
            sys.exit(f"invalid repeat or delay specified: {sys.argv[4]} {sys.argv[5]}")
    
    send_udp_packet(message, host, port, repeat, delay_ms)

if __name__ == "__main__":
    main()
