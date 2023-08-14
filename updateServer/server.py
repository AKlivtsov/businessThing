import socket

IP = '31.131.68.162'
PORT = 8080
ADDR = (IP, PORT)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()

    print("[STARTING] Server has been started and now listening.")
    print("[INFO] Server's addr is: " + str(IP) + ":"+ str(PORT))
    print("[INFO] You can change ip and port by editing server.py file")
 
    while True:
        conn, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        
        version = open(version.txt, "r")
        conn.send(version.encode("utf-8"))

 

        conn.send("File data received".encode("utf-8"))
 
        # завершаем
        file.close()
        conn.close()
        print(f"[DISCONNECTED] {addr} disconnected.")
 
if __name__ == "__main__":
    main()