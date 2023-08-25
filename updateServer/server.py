from _thread import *
from typing import Optional
import socket
import struct
import sqlite3
import pathlib
import os

sock = socket.socket()
IP = '127.0.0.1'
PORT = 1233
sock.bind((IP, PORT))

print('Waitiing for a Connection..')
sock.listen(5)


def getFileList(path):
    def clear():
            for item in mainList:
                if "." not in item:
                    mainList.pop(mainList.index(item))
                    clear()

    def pathCheck(dirList, startPath):
        for item in dirList:
            if "." not in item:
                newPath = startPath + '/' + item

                if not os.path.isfile(newPath):
                    newList = os.listdir(newPath)

                    for newItem in newList:
                        pathToCheck = []

                        if "." in newItem:
                            mainList.append(item + '/' + newItem)

                        else:
                            pathToCheck.append(item + '/' + newItem)

                        if pathToCheck:
                            for path in  pathToCheck:
                                anoPath = startPath +'/' 
                                pathCheck(pathToCheck, anoPath)
    
        return True     

    mainList = os.listdir(path)
    state = pathCheck(mainList, path)

    if state:
        clear()
        return mainList


def threaded_client(conn):

    connect = sqlite3.connect("server.db")
    cursor = connect.cursor()

    cursor.execute(f"SELECT version FROM server WHERE ROWID = ?", (1,))
    versionTemp = cursor.fetchone()
    
    if versionTemp != None:

        version = ""
        for i in versionTemp:
            version += str(i)

        conn.send(version.encode('utf-8'))

        while True:
            respond = conn.recv(2048).decode('utf-8')
            
            if respond == "True":
                listOfFiles = getFileList("testFolder")

                for file in listOfFiles:

                    conn.send(file.encode('utf-8'))

                    startSending = conn.recv(2048).decode('utf-8')
                    if startSending == "Ready!":
                        
                        with open("testFolder/" + file, 'rb') as f:
                            data = f.read()

                        print(f'Sending ({len(data)}): {data}')

                        send_msg(conn, data)

                        print('Receiving')

                        response_data = recv_msg(conn)
                        print(f'Response ({len(response_data)}): {response_data}')

                        print('Close\n')

    else:
        conn.send("[ERR] CANNOT GET ACTUAL VERSION".encode('utf-8'))

    conn.close()


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

while True:
    Client, address = sock.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
sock.close()
