from _thread import *
import socket
import sqlite3
import pathlib
import os

sock = socket.socket()
IP = '127.0.0.1'
PORT = 1233
sock.bind((IP, PORT))

print('Waitiing for a Connection..')
sock.listen(5)


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

        respond = conn.recv(2048).decode('utf-8')
            
        if respond == "True":

            cursor.execute(f"SELECT path FROM server WHERE ROWID = ?", (1,))
            pathTemp = cursor.fetchone()

            if pathTemp != None:

                path = ""
                for i in pathTemp:
                    path += str(i)

                # открываем файл
                update = open(path, "rb")
                data = update.read(1024)

                # отправляем имя файла и расширение 
                conn.send(path.encode("utf-8"))
                print("name sended")

                # отправляем файл
                while (data):
                    conn.send(data)
                    data = update.read(1024)

                # завершаем 
                update.close()
                conn.close()
                print("success")

            else:
                conn.send("[ERR] CANNOT GET PATH".encode('utf-8'))
                print(f"[ERR] CANNOT GET PATH [ on {address[0]}:{str(address[1])}]")

    else:
        conn.send("[ERR] CANNOT GET ACTUAL VERSION".encode('utf-8'))
        print(f"[ERR] CANNOT GET ACTUAL VERSION [ on {address[0]}:{str(address[1])}]")

    conn.close()


while True:

    Client, address = sock.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))

sock.close()
