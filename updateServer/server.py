import socket

from _thread import *
import threading

print_lock = threading.Lock()


def threaded(conn):
    while True:

        # data received from client
        data = conn.recv(1024)

        if not data:

            # lock released on exit
            print_lock.release()
            break

        # reverse the given string from client
        data = data[::-1]

        # send back reversed string to client
        conn.send(data)

    # connection closed
    conn.close()


def Main():
    host = "127.0.0.1"

    # reserve a port on your computer
    # in our case it is 12345 but it
    # can be anything
    port = 8080

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    print("socket binded to port", port)

    # put the socket into listening mode
    sock.listen(5)
    print("socket is listening")

    # a forever loop until client wants to exit
    while True:

        # establish connection with client
        conn, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])

        # Start a new thread and return its identifier
        start_new_thread(threaded, (conn,))
    sock.close()


if __name__ == '__main__':
    Main()
