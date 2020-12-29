import socket
import sys
import time
import msvcrt

# this is our ip address
ip = "127.0.0.1"
port = 7777
UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_sock.bind((ip, 13117))


def start_game(TCP_socket):
    message = TCP_socket.recv(2048)
    if not message:
        return
    print(message.decode('ascii'))
    now = time.time()
    stop = now + 10
    while time.time() < stop:
        print("im in while")
        c = msvcrt.getch()
        print(c)
        if time.time() < stop:
            TCP_socket.send(c)
    print("im not in while")
    message = TCP_socket.recv(2048)
    if not message:
        return
    print(message.decode('ascii'))


def main():
    print("Client started, listening for offer requests...")
    while True:
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        TCP_socket.bind((ip, port))
        data, addr = UDP_sock.recvfrom(7)
        if not data:
            continue
        magic_cookie = data[:4]
        message_type = data[4:5]
        server_port = int.from_bytes(data[-2:], byteorder='big')

        # make sure the offer is valid
        if int.from_bytes(magic_cookie, 'big') != int.from_bytes(b'\xfe\xed\xbe\xef', 'big') | int.from_bytes(message_type, 'big') != int.from_bytes(b'\x02', 'big'):
            continue

        print("Received offer from "+addr[0]+", attempting to connect...")
        TCP_socket.connect((addr[0], server_port))
        TCP_socket.send("Bytes Hunters\n".encode('ascii'))

        start_game(TCP_socket)
        print("Server disconnected, listening for offer requests...")


if __name__ == '__main__':
    main()
