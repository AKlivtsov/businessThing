# база
import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QDialog, QApplication, QTableWidgetItem, QColorDialog, QMenu
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, QThread, QObject, Qt, QDate
from PyQt6.QtGui import QColor, QAction

# окна
import mainUI
import editUI
import saveDialogUI

#прочее
import sqlite3


class ReadThread(QtCore.QThread):
    # row, column, color(r, g, b), note
    s_data = QtCore.pyqtSignal(int, int, int, int, int, str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.user = None

    def username(self, user):
        self.user = user

    def run(self):

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        cursor.execute(f"SELECT count(*) FROM {self.user}")
        count = cursor.fetchone()

        countTemp = ""
        for i in count:
            countTemp += str(i)
        count = int(countTemp)

        for index in range(count):
            if index != 0:

                # row, column
                cursor.execute(f"SELECT rowAndColumn FROM {self.user} WHERE ROWID = ?", (index,))
                rowAndColumnTemp = cursor.fetchone()

                rowAndColumn = ""
                for i in rowAndColumnTemp:
                    rowAndColumn += str(i)

                rowAndColumn = rowAndColumn.split(":")
                row = int(rowAndColumn[0])
                column = int(rowAndColumn[1])

                # notes
                cursor.execute(f"SELECT notes FROM {self.user} WHERE ROWID = ?", (index,))
                notesTemp = cursor.fetchone()

                notes = ""
                for i in notesTemp:
                    notes += str(i)

                # color
                cursor.execute(f"SELECT color FROM {self.user} WHERE ROWID = ?", (index,))
                colorTemp = cursor.fetchone()

                color = ""
                for i in colorTemp:
                    color += str(i)

                color = color.split(":")
                red = int(color[0])
                green = int(color[1])
                blue = int(color[2])

                self.s_data.emit(row, column, red, green, blue, notes)   


class SaveThread(QtCore.QThread):
    s_update = QtCore.pyqtSignal(str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.user = None
        self.table = None

    def username(self, user):
        self.user = user

    def setTable(self, table):
        self.table = table

    def run(self):

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        for column in range(self.table.columnCount()):

            for row in range(self.table.rowCount()): 
                cell = self.table.item(row, column)

                if cell:            
                    bg = self.table.item(row, column).background()
                    note = self.table.item(row, column).toolTip()

                    red, green, blue, _ = bg.color().getRgb()
                    color = f"{red}:{green}:{blue}"

                    rowAndColumn = f"{row}:{column}"

                    cursor.execute(f"SELECT rowAndColumn FROM {self.user} WHERE rowAndColumn = ?",
                        (rowAndColumn,))
                    
                    dbRowAndColumn = cursor.fetchone()

                    if dbRowAndColumn is None:       
                        cursor.execute(f"INSERT INTO {self.user}(rowAndColumn, notes, color) VALUES(?, ?, ?);",
                            (rowAndColumn, note, color) )

                        self.s_update.emit('upd')

                    else:
                        cursor.execute(f"UPDATE {self.user} SET notes = ? WHERE rowAndColumn = ?",
                            (note, rowAndColumn))

                        cursor.execute(f"UPDATE {self.user} SET color = ? WHERE rowAndColumn = ?", 
                            (color, rowAndColumn))

                        self.s_update.emit('upd')
                    
                    connect.commit()

        connect.close()
        self.s_update.emit('cls')


class SaveDialog(QtWidgets.QDialog, saveDialogUI.Ui_Dialog):
    def __init__(self):
        super(SaveDialog, self).__init__()
        self.setupUi(self)

    def setRange(self, range_):
        self.pb_save.setRange(0, range_)

    def add(self):
        self.pb_save.setValue(self.pb_save.value() + 1)


class MainWindow(QtWidgets.QMainWindow, mainUI.Ui_MainWindow, QDialog, QColor):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("BusinessThing")
        self.setTable()
        self.setBar()

        self.user = "DefaultTable"

        self.tw_table.cellClicked.connect(lambda: self.editWindow.show())
        # self.tw_table.cellDoubleClicked.connect(self.clearCell)

        self.btn_notes.clicked.connect(lambda: self.editWindow.show())
        self.btn_save.clicked.connect(self.save)

        self.editWindow = EditWindow()
        self.editWindow.mainInfo.connect(self.converter)

        self.readThread = ReadThread()
        self.readThread.s_data.connect(self.write)

        self.saveThread = SaveThread()
        self.saveThread.s_update.connect(self.dialogUpd)

        self.saveDialog = SaveDialog()

    def setTable(self):

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

    # TODO: make user change is able 
    def setBar(self):

        def makeAct(name, item):
            self.name = QAction(str(item), self)
            self.changeMenu.addAction(self.name)

        # CREATE TABLE DefaultTable (
        #   row     INTEGER,
        #   column_ INTEGER,
        #   notes   TEXT,
        #   color   INTEGER
        #   );

        menubar = self.menuBar()
        self.changeMenu = QMenu('сменить таблицу', self)

        self.loadAct = QAction('Загрузить', self)
        self.saveAct = QAction('Сохранить', self)
        self.m_file.addAction(self.saveAct)
        self.m_file.addAction(self.loadAct)

        self.saveAct.triggered.connect(self.save)
        self.loadAct.triggered.connect(self.commitUser)

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        cursor.execute("""SELECT name FROM sqlite_master WHERE type='table';""")

        tableList = cursor.fetchall()

        indexCount = 0

        for item in tableList:

            clearItem = ""
            for i in item:
                clearItem += str(i)

            tableList[indexCount] = clearItem
            makeAct(f"{tableList[indexCount]}Act", tableList[indexCount])

            self.m_file.addMenu(self.changeMenu)
            indexCount += 1

        indexCount = 0

    def setMenuOption(self, name):
        self.m_change

    def save(self):
        self.saveDialog.show()
        self.saveDialog.setRange(self.tw_table.columnCount() * self.tw_table.rowCount())

        self.saveThread.username(self.user)
        self.saveThread.setTable(self.tw_table)
        self.saveThread.start()

    def dialogUpd(self, msg):
        if msg == 'upd':
            self.saveDialog.add()
        else:
            self.saveDialog.close()
    
    def commitUser(self):
        self.readThread.username(self.user)
        self.readThread.start()

    # unite converter and write functions
    def write(self, row, column, red, green, blue, notes):
        self.tw_table.setItem(row, column, QTableWidgetItem())
        self.tw_table.item(row, column).setBackground(QtGui.QColor(red,green,blue))
        self.tw_table.item(row, column).setToolTip(notes)

    def converter(self, month, day, color, notes):    
        row = month - 1  
        column = day - 1

        self.tw_table.setItem(row, column, QTableWidgetItem())
        self.tw_table.item(row, column).setToolTip(notes)

        if color != None:
            self.tw_table.item(row, column).setBackground(color)
        else:
            self.tw_table.item(row, column).setBackground(QtGui.QColor(100,100,150))


class EditWindow(QtWidgets.QMainWindow, editUI.Ui_MainWindow, QDialog):
    mainInfo = QtCore.pyqtSignal(int, int, object, str)

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
