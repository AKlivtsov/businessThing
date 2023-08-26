import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication
from PyQt6.QtCore import QThread, QObject

# окно 
import launchUI

# программа
import main

# подключение
import socket

# прчоее
import tarfile as tar
import os

IP = '127.0.0.1'
PORT = 1233


class UpdateThread(QThread):
    s_highMsg = QtCore.pyqtSignal(str)
    s_lowMsg = QtCore.pyqtSignal(bool) 

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.localVersion = 0.2
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
    
                        if path != "ERR] CANNOT GET PATH":

                            try:
                                os.mkdir("exp")

                            except FileExistsError:
                                pass
    
                            file = open("exp/" + path, "wb")
    
                            self.s_highMsg.emit("Получаем обновление...")
    
                            while True:
                                data = conn.recv(1024)
                                file.write(data)
    
                                if not data:
                                    break
    
                            self.s_highMsg.emit("Устанавливаем обновление...")
                            file.close()

                            update = tar.open("exp/update.tar", 'r:gz')
                            update.extractall()
    
                        else:
                            self.s_highMsg.emit(path)
    
                    else:
                        self.s_highMsg.emit(version)

                    self.s_lowMsg.emit(True)

        except ConnectionRefusedError:
            self.s_highMsg.emit("Не удаётся подключится к серверу обновлений.")
            self.s_lowMsg.emit(True)


class MainWindow(QMainWindow, launchUI.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon('assets/icon96px.ico'))
        self.setWindowTitle("Запуск")

        self.setFixedWidth(670)
        self.setFixedHeight(300)

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

    def startMainApp(self, state):
        if state:
            self.lbl_status.setText("Запуск...")

            # path to main file
            sys.path.insert(1, 'testFolder/test1/testttt/xcx')

            import asd # simple py files executes automaticly 

            # for pyqt progs:
            # main = main.MainWindow()
            # main.show()  

            self.close()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
