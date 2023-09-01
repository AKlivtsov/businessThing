import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QThread, QObject, QSize

# окно 
import launchUI

# подключение
import socket

# прчоее
import tarfile as tar
import pathlib
import os

IP = '127.0.0.1'
PORT = 1233


class UpdateThread(QThread):
    s_highMsg = QtCore.pyqtSignal(str)
    s_lowMsg = QtCore.pyqtSignal(bool, str) 
    s_path = QtCore.pyqtSignal(str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.localVersion = 0.2 # extract from db
        self.update = False

    def run(self):
        try:
            with socket.create_connection((IP, PORT)) as conn:
                version = conn.recv(2048).decode('utf-8')
    
                if version != '[ERR] CANNOT GET ACTUAL VERSION':
    
                    if self.localVersion < float(version):
                        self.s_highMsg.emit("Обновлеение запрошенно")
                        conn.send("True".encode('utf-8'))
                        self.update = True
    
                    else: 
                        self.s_highMsg.emit("У вас установлена последняя версия")
            
                    if self.update:
                        path = conn.recv(2048).decode('utf-8')
    
                        if path != "[ERR] CANNOT GET PATH":
                            filename = pathlib.PurePath(path).name
                            file = open(path, "wb")
    
                            self.s_highMsg.emit("Получаем обновление...")
    
                            while True:
                                data = conn.recv(1024)
                                file.write(data)
    
                                if not data:
                                    break
    
                            self.s_highMsg.emit("Устанавливаем обновление...")
                            file.close()

                            update = tar.open(filename, 'r:gz')
                            update.extractall()
    
                        else:
                            self.s_highMsg.emit(path)
    
                    else:
                        self.s_highMsg.emit(version)

                    self.s_lowMsg.emit(True, filename)

        except ConnectionRefusedError:
            self.s_highMsg.emit("Не удаётся подключится к серверу обновлений.")
            self.s_lowMsg.emit(True, "ver1_2") # automaticly set folder


class MainWindow(QMainWindow, launchUI.Ui_MainWindow, QSize):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon('assets/icon96px.ico'))
        self.setWindowTitle("Запуск")

        self.setFixedSize(QSize(670, 300))

        self.lbl_status.setText("Запуск проверки обновления...")

        self.refusedConn = False

        self.updateThread = UpdateThread()
        self.updateThread.s_highMsg.connect(self.updateLabel)
        self.updateThread.s_lowMsg.connect(self.startMainApp)

        self.updateThread.start()

    def updateLabel(self, msg):
        self.lbl_status.setText(msg)

        if msg == "Не удаётся подключится к серверу обновлений.":
            self.refusedConn = True

    def startMainApp(self, state, filename):
        if state:
            self.lbl_status.setText("Запуск...")

            sys.path.insert(1, f'{filename}/')

            import main
            app = main.MainWindow()
            app.show()

            self.close()  


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
