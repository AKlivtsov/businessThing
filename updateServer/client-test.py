import socket

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

    else: 
        print("i'am ia up to date!")

    while True:
        msg = input('Say Something: ')
        sock.send(str.encode(msg))
        Response = sock.recv(1024)
        print(Response.decode('utf-8'))
else:
    print(version)
sock.close()