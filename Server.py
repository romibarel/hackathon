import socket
import time
import threading
from random import seed
from random import randint


# this is our ip address
ip = "127.0.0.1"
UDP_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDP_sock.bind((ip, 2084))
TCP_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
TCP_socket.bind((ip, 2084))
TCP_socket.setblocking(False)
group1 = list()
group2 = list()
client_threads = list()
score1 = [0]
score2 = [0]
thread_lock1 = threading.Lock()
thread_lock2 = threading.Lock()


# this function is run by the sending thread to send joining offers
def send():
    try:
        now = time.time()
        stop = now + 10
        while time.time() < stop:
            # destination port 13117
            # Magic cookie (4 bytes): 0xfeedbeef. The message is rejected if it doesn’t start with this cookie
            # Message type (1 byte): 0x2 for offer. No other message types are supported.
            # Server port (2 bytes): The port on the server that the client is supposed to connect to over
            # TCP (the IP address of the server is the same for the UDP and TCP connections,
            # so it doesn't need to be sent).
            UDP_sock.sendto(b'\xfe\xed\xbe\xef\x02\x08\x24', (ip, 13117))
            time.sleep(1)
    except:
        print("something went wrong in sending offers")


def server_listen():
    try:
        TCP_socket.listen()
        now = time.time()
        stop = now + 10
        while time.time() < stop:
            try:
                client_socket, addr = TCP_socket.accept()
                client_socket.setblocking(False)
            except:
                continue
            # with client_socket:
            name = ""
            while True:
                # put together the name of the tea
                try:
                    next_char = client_socket.recv(1)
                except:
                    continue
                if not next_char:
                    break
                name += str(next_char.decode('ascii'))
                if name.endswith('\n'):
                    # generate 1 or 0 randomly to decide which team the clients is added to
                    chance = randint(0, 1)
                    if chance == 0:
                        group1.append((name, client_socket, addr))
                        print(name + " group 1 " + str(len(group1)))
                    else:
                        group2.append((name, client_socket, addr))
                        print(name + " group 2 " + str(len(group2)))
                    break

    except:
        print("something went wrong in listening ")


def send_invites():
    sending = threading.Thread(target=send, args=())
    listening = threading.Thread(target=server_listen, args=())
    sending.start()
    listening.start()
    # continue to the next function only when both threads finish their jobs
    time.sleep(10)


def start_game():
    print("started game - server")
    score1[0] = 0
    score2[0] = 0
    print(str(score1[0]) +" "+ str(score2[0]))
    message = "Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
    # t = (name, client_socket, addr)
    for t in group1:
        message += t[0] + "\n"

    message += "Group 2:\n==\n"
    for t in group2:
        message += t[0] + "\n"

    message += "\nStart pressing keys on your keyboard as fast as you can!!\n"
    print(message)
    # for each team in both groups start catching keys
    for t in group1:
        client_threads.append(threading.Thread(target=catch_keys, args=(t, message, 1,)))

    for t in group2:
        client_threads.append(threading.Thread(target=catch_keys, args=(t, message, 2,)))
    print(str(len(client_threads)))

    # start all the threads and wait for all of them to end
    for t in client_threads:
        print("hi im starting")
        t.start()
        print("hi i started")
    for t in client_threads:
        print("im waiting")
        t.join()

    end_message = "Game over!\nGroup 1 typed in "+str(score1[0])+" characters. Group 2 typed in "+str(score2[0]) + \
                  " characters.\n"
    if score1[0] > score2[0]:
        end_message += "Group 1 wins!\n\nCongratulations to the winners:\n=="
        for t in group1:
            end_message += "\n" + t[0]
    elif score1[0] < score2[0]:
        end_message += "Group 2 wins!\n\nCongratulations to the winners:\n=="
        for t in group2:
            end_message += "\n" + t[0]
    else:
        end_message += "IT'S A TIE!!!\nCongratulations to EVERYONE!!!!!"

    # create new threads to share the results
    client_threads.clear()
    for t in group1:
        client_threads.append(threading.Thread(target=end_game, args=(t, end_message,)))
    for t in group2:
        client_threads.append(threading.Thread(target=end_game, args=(t, end_message,)))
    # start all the threads and wait for all of them to end
    for t in client_threads:
        t.start()
    for t in client_threads:
        t.join()

    # reset the game and announce end
    group1.clear()
    group2.clear()
    client_threads.clear()
    print("Game over, sending out offer requests...")


# client_tuple = (name, client_socket, addr)
def end_game(client_tuple, message):
    print(message)
    try:
        client_socket = client_tuple[1]
        client_socket.send(str(message).encode('ascii'))
        client_socket.close()
    except:
        print("something went wrong in ending the game")


# client_tuple = (name, client_socket, addr)
def catch_keys(client_tuple, message, group):
    print("hi im catch keys")
    try:
        counter = 0
        client_socket = client_tuple[1]
        client_socket.send(str(message).encode('ascii'))
        now = time.time()
        stop = now + 10
        while time.time() < stop:
            try:
                key = client_socket.recv(1)
            except:
                continue
            if not key:
                break
            print(key)
            counter += 1
        if group == 1:
            thread_lock1.acquire()
            score1[0] += counter
            thread_lock1.release()
        else:
            thread_lock2.acquire()
            score2[0] += counter
            thread_lock2.release()
    except:
        print("something went wrong in catching keys")

def main():
    print("Server started, listening on IP address " + ip)
    # plant seed to generate random integers
    seed(1)
    while True:
        try:
            send_invites()
            start_game()
        except:
            print("something went wrong in main")


if __name__ == '__main__':
    main()