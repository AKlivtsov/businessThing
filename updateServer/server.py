import socket
import os

# БД
import sqlite3


class Server():
    def __init__(self):

        self.IP = '31.131.68.162'
        self.PORT = 8080
        self.ADDR = (self.IP, self.PORT)

    def execute(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(self.ADDR)
        server.listen()

        print("[STARTING] Server has been started and now listening.")
        print("[INFO] Server's addr is: " + str(self.IP) + ":"+ str(self.PORT))
        print("[INFO] You can change ip and port by editing server.py file")
 
        while True:
            conn, addr = server.accept()
            print(f"[NEW CONNECTION] {addr} connected.")
        
            version = open(version.txt, "r")
            conn.send(version.encode("utf-8"))

 

            conn.send("File data received".encode("utf-8"))
 
            file.close()
            conn.close()
            print(f"[DISCONNECTED] {addr} disconnected.")

 
if __name__ == "__main__":
    s = Server()
    s.execute()
