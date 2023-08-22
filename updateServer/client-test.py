import socket
import os

IP = '127.0.0.1'
PORT = 1233

localVersion = 0.2

sock = socket.socket()
sock.connect((IP, PORT))

version = sock.recv(2048).decode('utf-8')

if version != '[ERR] CANNOT GET ACTUAL VERSION':
    print(f"actual version is: {version}")

    if localVersion < float(version):
        print("update me!")
        sock.send("True".encode('utf-8'))

    else: 
        print("i'am is up to date!")

    while True:
        path = sock.recv(2048).decode('utf-8')
        print(f"Working on: {path}")

        if "/" in path:
            filename = path.split("/")[-1]
            folders = path.replace(filename, '')
            folders = "exportFolder/" + folders

            try:
                os.makedirs(folders)

            except FileExistsError:
                pass

            file = open(folders + filename, "wb")

        else:

            try:
                os.mkdir("exportFolder/")

            except FileExistsError: 
                pass

            filename = path.split("/")[-1]
            file = open("exportFolder/" + filename, "wb")

        while True:
            data = sock.recv(1024)
            print(f"data of {file}:\n {data}")
            file.write(data)

            if not data:
                break

        file.close()

        msg = sock.recv(2048).decode('utf-8')
        if msg == "[DONE]":
            print(msg)
            break
        
else:
    print(version)

sock.close()