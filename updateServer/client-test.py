from typing import Optional
import socket
import struct
import os

IP = '127.0.0.1'
PORT = 1233

update = False
localVersion = 0.2


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

        
        if update:
            path = conn.recv(2048).decode('utf-8')
            file = open("exp/" + path, "wb")
            print(f"Working on: {path}")
 
            print(f"[RECV] Receiving the file data.")

            while True:
                data = conn.recv(1024)
                file.write(data)

                if not data:
                    break

            print(f"[DONE] The file is received successfuly.")
 
            # завершаем
            file.close()
            conn.close()

    else:
        print(version)
