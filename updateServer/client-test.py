import socket
import struct
import os

IP = '127.0.0.1'
PORT = 1233

update = False
localVersion = 0.2

def receive_file_size(sck: socket.socket):
    fmt = "<Q"
    expected_bytes = struct.calcsize(fmt)
    received_bytes = 0
    stream = bytes()

    while received_bytes < expected_bytes:
        chunk = sck.recv(expected_bytes - received_bytes)
        stream += chunk
        received_bytes += len(chunk)

    filesize = struct.unpack(fmt, stream)[0]

    return filesize

def receive_file(sck: socket.socket, filename, filesize):

    with open(filename, "wb") as f:
        received_bytes = 0

        while received_bytes < filesize:
            chunk = sck.recv(1024)

            if chunk:
                f.write(chunk)
                received_bytes += len(chunk)

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
                    conn.send("Done".encode('utf-8'))

                else:
                    filename = path.split("/")[-1]

                    try:
                        os.mkdir("exportFolder/")
                    except FileExistsError: 
                        pass

                    conn.send("Done".encode('utf-8'))

                filesize = receive_file_size(conn)
                print(filesize)
                conn.send("DoneEnd".encode('utf-8'))

                with open("exportFolder/" + filename, "wb") as f:
                    received_bytes = 0

                    while received_bytes < filesize:
                        chunk = conn.recv(1024)
                        print(chunk)

                        if chunk:
                            f.write(chunk)
                            received_bytes += len(chunk)

                print("s")

    else:
        print(version)
