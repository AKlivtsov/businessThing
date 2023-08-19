import sys
from PyQt6 import QtWidgets, QtCore, QtGui

# окно 
import launchUI

# программа
import main

# подключение
import socket

IP = '31.131.68.162'
PORT = 8080
ADDR = (IP, PORT)


class MainWindow(QMainWindow, launchUI.Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
