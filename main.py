# база
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QApplication, QTableWidgetItem, QColorDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, QThread, QObject, Qt
from PyQt6.QtGui import QColor

# окна
import mainUI
import editUI

#прочее
import sqlite3

# основное окно
class MainWindow(QtWidgets.QMainWindow, mainUI.Ui_MainWindow, QDialog, QColor):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("BusinessThing")
        self.settingTable()

        self.tw_table.cellClicked.connect(self.cellWasClicked)
        self.tw_table.cellDoubleClicked.connect(self.clearCell)

        self.btn_notes.clicked.connect(self.edit)

        self.editWindow = EditWindow()
        self.editWindow.mainInfo.connect(self.converter)

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
        self.editWindow.show()

    def update(self, satate):
        print(state)

    def converter(self, monthIn, dayIn, monthOut, dayOut):
        '''
        print(monthIn)
        print(dayIn)
        print(monthOut)
        print(dayOut)
        
        x = dayOut-dayIn

        print(x)

        for day in range(x):
            self.tw_table.setItem(0, day, QTableWidgetItem())
            self.tw_table.item(0, day).setBackground(QtGui.QColor(100,100,150))'''




# окно изменения
class EditWindow(QtWidgets.QMainWindow, editUI.Ui_MainWindow, QDialog):
    mainInfo = QtCore.pyqtSignal(int, int, int, int)
    otherInfo = QtCore.pyqtSignal(str)

    def __init__(self):
        super(EditWindow, self).__init__()
        self.setupUi(self)

        self.btn_color.clicked.connect(self.colorDialog)
        self.btn_save.clicked.connect(self.save)
        
        self.color = None
        self.monthIn = None
        self.monthOut = None
        self.dayIn = None
        self.dayOut = None
        self.timeIn = None
        self.timeOut = None
        self.notes = None

    def colorDialog(self):
        self.color = QColorDialog.getColor()

    def save(self):
        self.monthIn = self.date_in.date().month()
        self.monthOut = self.date_out.date().month()
        self.dayIn = self.date_in.date().dayOfYear()
        self.dayOut = self.date_out.date().dayOfYear()

        self.monthDaysIn = self.date_in.date().daysInMonth()
        self.monthDaysOut = self.date_out.date().daysInMonth()

        days = self.dayOut - self.dayIn
        monthCount = self.monthDaysIn

        for day in range(days):
            if day <= monthCount:
                print(f"draw day: {day} in month: {monthCount}")
            else:
                days -= monthCount
                monthCount.addMonths(1)

        self.mainInfo.emit(self.monthIn, self.dayIn, self.monthOut, self.dayOut)

        self.timeIn = self.time_in.time().toString(Qt.DateFormat.ISODate)
        self.timeOut = self.time_out.time().toString(Qt.DateFormat.ISODate)

        self.notes = self.te_notes.toPlainText()
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
