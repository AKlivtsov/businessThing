# база
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QApplication, QTableWidgetItem, QColorDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, QThread, QObject

# окна
import mainUI
import editUI

#прочее
import sqlite3

# основное окно
class MainWindow(QtWidgets.QMainWindow, mainUI.Ui_MainWindow, QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.settingTable()
        self.setWindowTitle("BusinessThing")

        self.tw_table.cellClicked.connect(self.cellWasClicked)
        self.tw_table.cellDoubleClicked.connect(self.clearCell)

        self.btn_notes.clicked.connect(self.edit)

    def settingTable(self):

        self.tw_table.setRowCount(12)
        self.tw_table.setColumnCount(31)

        for i in range(31):
            self.tw_table.setColumnWidth(i, 5)

        self.tw_table.setLineWidth(5)

        monthTyple = (
            'Январь', 'Февраль','Март',
            'Апрель','Май','Июнь',
            'Июль','Август','Сентябрь',
            'Октябрь','Ноябрь','Декабрь',
            )
        
        self.tw_table.setVerticalHeaderLabels(monthTyple)

    def cellWasClicked(self, row, column):
        self.tw_table.setItem(row, column, QTableWidgetItem())
        self.tw_table.item(row, column).setBackground(QtGui.QColor(100,100,150))

    def clearCell(self, row, column):
        self.tw_table.setItem(row, column, QTableWidgetItem())

    def edit(self):
        self.e = EditWindow()
        self.e.show()


# окно изменения
class EditWindow(QtWidgets.QMainWindow, editUI.Ui_MainWindow, QDialog):
    def __init__(self):
        super(EditWindow, self).__init__()
        self.setupUi(self)

        self.btn_color.clicked.connect(self.color)

    def color(self):
        color = QColorDialog.getColor()
        print(color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
