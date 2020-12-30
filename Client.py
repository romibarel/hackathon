import socket
import sys
import os
import time
import getch
from scapy.arch import get_if_addr
from colorama import *


# this is our ip address
ip = get_if_addr('eth1')
port = 13117


def start_game(TCP_socket):
    message = TCP_socket.recv(2048)
    if not message:
        return
    print(message.decode('ascii'))
    now = time.time()
    stop = now + 10
    while time.time() < stop:
        c = getch.getch()
        if time.time() < stop:
            TCP_socket.send(c.encode('ascii'))
    message = TCP_socket.recv(2048)
    if not message:
        return
    print(message.decode('ascii'))


def main():
    print("Client started, listening for offer requests...")
    while True:
        UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        UDP_sock.bind((ip, 13117))
        TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TCP_socket.bind((ip, port))
        data, addr = UDP_sock.recvfrom(7)
        if not data:
            continue
        UDP_sock.close()
        #decode the data
        magic_cookie = data[:4]
        message_type = data[4:5]
        server_port = int.from_bytes(data[-2:], byteorder='big')

        #make sure the offer is valid
        if int.from_bytes(magic_cookie, 'big') != int.from_bytes(b'\xfe\xed\xbe\xef', 'big') | int.from_bytes(message_type, 'big') != int.from_bytes(b'\x02', 'big'):
            continue

        print("Received offer from "+addr[0]+", attempting to connect...")
        TCP_socket.connect((addr[0], server_port))
        TCP_socket.send("Cookie Monsters\n".encode('ascii'))

        start_game(TCP_socket)
        print("Server disconnected, listening for offer requests...")


if __name__ == '__main__':
    main()
