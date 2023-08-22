from _thread import *
import socket
import os
import sqlite3
import pathlib

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

def sendMagic(file):
    # отправляем путь, имя и расширние фалйа
    connection.send(file.encode("utf-8"))

    # открываем файл
    openedFile = open(file, "rb")
    data = openedFile.read(1024)

    # отправляем файл
    while (data):
        connection.send(data)
        data = openedFile.read(1024)

    # завершаем 
    openedFile.close()

def threaded_client(connection):

    connect = sqlite3.connect("server.db")
    cursor = connect.cursor()

    cursor.execute(f"SELECT version FROM server WHERE ROWID = ?", (1,))
    versionTemp = cursor.fetchone()
    
    if versionTemp != None:

        version = ""
        for i in versionTemp:
            version += str(i)

        connection.send(version.encode('utf-8'))

        while True:
            respond = connection.recv(2048).decode('utf-8')
            
            if respond == "True":
                listOfFiles = getFileList("testFolder")

                for file in listOfFiles:
                    # отправляем путь, имя и расширние фалйа
                    connection.send(file.encode("utf-8"))

                    # открываем файл
                    print(f"Working on: {file}              | for {address[0]}:{str(address[1])}")
                    openedFile = open("testFolder/" + file, "rb")
                    data = openedFile.read(1024)
                    print(f" data of {file} :\n    {data}")
                    print('\n')

                    # отправляем файл
                    while (data):
                        connection.send(data)
                        data = openedFile.read(1024)

                    # завершаем 
                    openedFile.close()

                connection.close()

    else:
        connection.send("[ERR] CANNOT GET ACTUAL VERSION".encode('utf-8'))

    connection.close()

while True:
    Client, address = sock.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
sock.close()
