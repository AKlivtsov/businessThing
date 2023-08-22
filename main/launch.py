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

IP = '127.0.0.1'
PORT = 8080
ADDR = (IP, PORT)


class MainWindow(QMainWindow, launchUI.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon('assets/icon96px.ico'))
        self.setWindowTitle("Запуск")

        self.setFixedWidth(670)
        self.setFixedHeight(300)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
