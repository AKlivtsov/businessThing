import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication 
from PyQt6.QtCore import QThread, QObject, QSize

# окно
import launchUI

# подключение
import socket

# прочее
import tarfile as tar
import pathlib
import shutil
import sqlite3
import os
import subprocess

IP = "127.0.0.1"
PORT = 1233

def stringCleaner(string: str) -> str :
    newString = ""
    for i in string:
        newString += str(i)
    return newString


class UpdateThread(QThread):
    s_highMsg = QtCore.pyqtSignal(str)
    s_lowMsg = QtCore.pyqtSignal(bool, str)
    s_path = QtCore.pyqtSignal(str)

    def __init__(self):
        QtCore.QThread.__init__(self)

    def run(self):
        connect = sqlite3.connect("/Users/a.klivtsov/Desktop/CodieStuff/businessThing/MVVMTest/ver1_3/launch.db")
        cursor = connect.cursor()

        cursor.execute("SELECT localVersion FROM versionData WHERE ROWID = ?", (1,))
        localVersion = cursor.fetchone()

        if localVersion is not None:
            localVersion = float(stringCleaner(localVersion))

            try: #TODO: rework like guard 'n' raise in swift
                with socket.create_connection((IP, PORT)) as conn:
                    version = conn.recv(2048).decode("utf-8")
                    if version != "[ERR] CANNOT GET ACTUAL VERSION":
                        if localVersion < float(version):
                            
                            #TODO: save database (or old version)
                            
                            # ------удаляем старую версию -------------------
                            cursor.execute(
                                "SELECT path FROM versionData WHERE ROWID = ?", (1,)
                            )
                            path = stringCleaner(cursor.fetchone())
                            shutil.rmtree(path)

                            file = path + ".tar"
                            if os.path.isfile(file):
                                os.remove(file)

                            self.s_highMsg.emit("Обновлеение запрошенно")
                            conn.send("True".encode("utf-8"))

                            path = conn.recv(2048).decode("utf-8")

                            if path != "[ERR] CANNOT GET PATH":
                                # ------скачиваем обновление -------------------
                                filename = pathlib.PurePath(path).name
                                file = open(path, "wb")

                                self.s_highMsg.emit("Получаем обновление...")

                                while True:
                                    data = conn.recv(1024)
                                    file.write(data)

                                    if not data:
                                        break

                                # ------распаковка обновления --------------------
                                self.s_highMsg.emit("Устанавливаем обновление...")
                                file.close()

                                update = tar.open(filename, "r:gz")
                                update.extractall()
                                update.close()

                                fileName = filename.split(".")[-1]
                                path = filename.replace(f".{fileName}", "")

                                cursor.execute(
                                    "UPDATE versionData SET path = ? WHERE ROWID = ?",
                                    (path, 1),
                                )
                                connect.commit()
                                self.s_lowMsg.emit(True, path)
                                os.remove(filename)
                            else:
                                self.s_highMsg.emit("Ошибка обновления.")
                        else:
                            self.s_highMsg.emit("У вас установлена последняя версия")
                    else:
                        self.s_highMsg.emit("Ошибка обновления.")

            except ConnectionRefusedError:
                self.s_highMsg.emit("Не удаётся подключится к серверу обновлений.")

                cursor.execute("SELECT path FROM versionData WHERE ROWID = ?", (1,))
                path = stringCleaner(cursor.fetchone())
                self.s_lowMsg.emit(True, path)

        else:
            self.s_highMsg.emit("Ошибка базы данных. Переустанвоите программу.")

        connect.close()


class MainWindow(QMainWindow, launchUI.Ui_MainWindow, QSize):
    startMsg = QtCore.pyqtSignal(bool)
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon("assets/icon96px.ico"))
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

    def startMainApp(self, state):
        if state:
            self.lbl_status.setText("Запуск...")
            self.startMsg.emit(True)
            self.close()
            subprocess.run(["chmod", "-R", "777", "ver1_3/main.py"]) #! if error with permissions
            subprocess.run(["python3","ver1_3/main.py"]) #! change to exe when finished
            
            
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())        
