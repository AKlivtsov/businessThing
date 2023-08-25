from typing import Optional
import socket
import struct
import os

IP = '127.0.0.1'
PORT = 1233

update = False
localVersion = 0.2


def send_msg(sock, msg):
    # Prefix each message with a 8-byte length (network byte order)
    msg = struct.pack('>Q', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock) -> Optional[bytes]:
    # 8-byte
    payload_size = struct.calcsize(">Q")

    # Read message length and unpack it into an integer
    raw_msg_len = recv_all(sock, payload_size)
    if not raw_msg_len:
        return None

    msg_len = struct.unpack('>Q', raw_msg_len)[0]

    # Read the message data
    return recv_all(sock, msg_len)


def recv_all(sock, n) -> Optional[bytes]:
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()

    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None

        data += packet

    return bytes(data)


with socket.create_connection((IP, PORT)) as conn:
    version = conn.recv(2048).decode('utf-8')

    if version != '[ERR] CANNOT GET ACTUAL VERSION':
        print(f"actual version is: {version}")

        if localVersion < float(version):
            print("update me!")
            conn.send("True".encode('utf-8'))
            update = True

        else: 
            print("i'am is up to date!")

        while True:
            if update:
                path = conn.recv(2048).decode('utf-8')
                print(f"Working on: {path}")

                if "/" in path:
                    filename = path.split("/")[-1]
                    folders = path.replace(filename, '')
                    folders = "exportFolder/" + folders

                    try:
                        os.makedirs(folders)
                    except FileExistsError:
                        pass
                    conn.send("Ready!".encode('utf-8'))

                else:
                    filename = path.split("/")[-1]

                    try:
                        os.mkdir("exportFolder/")
                    except FileExistsError: 
                        pass
                    conn.send("Ready!".encode('utf-8'))

                data = recv_msg(conn)
                print('Receiving ({}): {}'.format(len(data), data))

                text = 'Ok! Message size: {}'.format(len(data))
                print('Sending: {}'.format(text))

                rs = bytes(text, 'utf-8')
                send_msg(conn, rs)

                print('Close\n')

    else:
        print(version)
