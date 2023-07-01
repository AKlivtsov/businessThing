# база
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QApplication, QTableWidgetItem, QColorDialog
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, QThread, QObject, Qt, QDate
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

        self.tw_table.cellClicked.connect(self.edit)
        self.tw_table.cellDoubleClicked.connect(self.clearCell)

        self.btn_notes.clicked.connect(self.edit)

        self.editWindow = EditWindow()
        self.editWindow.mainInfo.connect(self.converter)

    def settingTable(self):

        self.tw_table.setRowCount(12)
        self.tw_table.setColumnCount(31)

        for i in range(31):
            self.tw_table.setColumnWidth(i, 20)

        self.tw_table.setLineWidth(10)

        monthTyple = (
            'Январь', 'Февраль','Март',
            'Апрель','Май','Июнь',
            'Июль','Август','Сентябрь',
            'Октябрь','Ноябрь','Декабрь',
            )
        
        self.tw_table.setVerticalHeaderLabels(monthTyple)

    #TODO: replace print with DB stuff and rename to "save"
    #TODO: also make DB with all months and days
    #TODO: delete row and column from func arguments
    def clearCell(self, row, column):

        for column in range(self.tw_table.columnCount()):

            for row in range(self.tw_table.rowCount()): 
                cell = self.tw_table.item(row, column)

                if cell:            
                    bg = self.tw_table.item(row, column).background()
                    note = self.tw_table.item(row, column).toolTip()

                    print(f"====================================")
                    print(f'row: {row}, column: {column}, bg={bg}')
                    print(f"ToolTip: {note}")
                    print(f"====================================")

    def edit(self):
        self.editWindow.show()

    def converter(self, month, day, color, notes):    
        row = month - 1  
        column = day - 1

        self.tw_table.setItem(row, column, QTableWidgetItem())
        self.tw_table.item(row, column).setToolTip(notes)

        if color != None:
            self.tw_table.item(row, column).setBackground(color)
        else:
            self.tw_table.item(row, column).setBackground(QtGui.QColor(100,100,150))


# окно изменения
class EditWindow(QtWidgets.QMainWindow, editUI.Ui_MainWindow, QDialog):
    mainInfo = QtCore.pyqtSignal(int, int, object, str)
    otherInfo = QtCore.pyqtSignal(str)

    def __init__(self):
        super(EditWindow, self).__init__()
        self.setupUi(self)
 
        self.date_in.setDate(QDate.currentDate())
        self.date_out.setDate(QDate.currentDate())

        self.btn_color.clicked.connect(self.colorDialog)
        self.btn_save.clicked.connect(self.save)
        
        self.color = None
        self.notes = None

    def colorDialog(self):
        self.color = QColorDialog.getColor()

    def save(self):
        notes = self.te_notes.toPlainText()
        timeIn = self.time_in.time().toString(Qt.DateFormat.ISODate)
        timeOut = self.time_out.time().toString(Qt.DateFormat.ISODate)

        notes = f"Заезд: {timeIn}\nВыезд: {timeOut}\n\n{notes}"

        dayOut = self.date_out.date().dayOfYear()
        monthCount = self.date_in.date()
        day = self.date_in.date().day()
        curDay = self.date_in.date()
        addedMonths = 0
        addedDays = 0

        workie = True

        while workie:

            if curDay.dayOfYear() <= dayOut:

                if day <= monthCount.daysInMonth():
                    month = monthCount.month()
                    self.mainInfo.emit(month,day, self.color, notes)
                    day += 1
                    addedDays += 1
                    curDay = self.date_in.date().addDays(addedDays) 

                else:
                    day = 1
                    addedMonths += 1
                    monthCount = self.date_in.date().addMonths(addedMonths)

            else:
                monthCount = self.date_in.date()
                day = self.date_in.date().day()
                curDay = self.date_in.date()
                addedMonths = 0
                addedDays = 0
                workie = False

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
