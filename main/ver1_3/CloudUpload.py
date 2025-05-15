import socket 

IP = "127.0.0.1"
PORT = 1233



def upload():
    try:
        with socket.create_connection((IP, PORT)) as conn:

            upload = conn.send(2048).encode("utf-8")
            isUploadPossible = conn.recv(2048).decode("utf-8")

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
            
            if isUploadPossible:
                file = open(path, "wb")
                data = conn.send(1024)

    except ConnectionRefusedError:
        print("Connection refused")