from _thread import *
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
                    print("file is: " + file)
                    conn.send(file.encode('utf-8'))

                    response = conn.recv(2048).decode('utf-8')
                    if response == "Done":
                        print('yep')

                        filesize = os.path.getsize("testFolder/" + file)
                        conn.sendall(struct.pack("<Q", filesize))

                        response = conn.recv(2048).decode('utf-8')
                        if response == "DoneEnd":
                            print('yepEnd')
                   
                            with open("testFolder/" + file, "rb") as f:
                                while read_bytes := f.read(1024):
                                    print(read_bytes)
                                    conn.sendall(read_bytes)

                conn.close()

    else:
        conn.send("[ERR] CANNOT GET ACTUAL VERSION".encode('utf-8'))

    conn.close()

while True:
    Client, address = sock.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
sock.close()
