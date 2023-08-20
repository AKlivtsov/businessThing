from _thread import *
import socket
import os
import sqlite3

sock = socket.socket()
IP = '127.0.0.1'
PORT = 1233
sock.bind((IP, PORT))

print('Waitiing for a Connection..')
sock.listen(5)

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
            data = connection.recv(2048).decode('utf-8')
            print(data)

            if not data:
                break

            reply = 'Server Says: ' + data
            connection.sendall(str.encode(reply))

    else:
        connection.send("[ERR] CANNOT GET ACTUAL VERSION".encode('utf-8'))

    connection.close()

while True:
    Client, address = sock.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(threaded_client, (Client, ))
sock.close()
