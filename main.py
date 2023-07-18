import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QDialog, QApplication, QTableWidgetItem, QColorDialog, QMessageBox, QMenu
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QTimer, QThread, QObject, Qt, QDate
from PyQt6.QtGui import QColor, QAction

# окна
import mainUI
import editDialogUI
import saveDialogUI
import createDialogUI
import deleteDialogUI
import reportDialogUI

#прочее
from memory_profiler import profile      # Use @profile to check memory consumption
import sqlite3
import time


class ReadThread(QThread):
    # row, column, color(r, g, b), note
    s_data = QtCore.pyqtSignal(int, int, int, int, int, str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.tableName = None

    def setTableName(self, tableName):
        self.tableName = tableName

    def run(self):

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        cursor.execute(f"SELECT count(*) FROM {self.tableName}")
        count = cursor.fetchone()

        countTemp = ""
        for i in count:
            countTemp += str(i)
        count = int(countTemp)

        for index in range(count + 1):
            if index != 0:

                # column
                cursor.execute(f"SELECT day FROM {self.tableName} WHERE ROWID = ?", (index,))
                column = cursor.fetchone()

                if column != None:

                    columnTemp = ""
                    for i in column:
                        columnTemp += str(i)
                    column = int(columnTemp)

                    cursor.execute(f"SELECT month FROM {self.tableName} WHERE ROWID = ?", (index,))
                    row = cursor.fetchone()

                    rowTemp = ""
                    for i in row:
                        rowTemp += str(i)
                    row = int(rowTemp)

                    # notes
                    cursor.execute(f"SELECT notes FROM {self.tableName} WHERE ROWID = ?", (index,))
                    notesTemp = cursor.fetchone()

                    if notesTemp != None:

                        notes = ""
                        for i in notesTemp:
                            notes += str(i)

                    else:
                        notes = None

                    # color
                    cursor.execute(f"SELECT color FROM {self.tableName} WHERE ROWID = ?", (index,))
                    colorTemp = cursor.fetchone()

                    if colorTemp != None:

                        color = ""
                        for i in colorTemp:
                            color += str(i)

                        color = color.split(":")
                        red = int(color[0])
                        green = int(color[1])
                        blue = int(color[2])

                    else:
                        red = None
                        green = None
                        blue = None

                    self.s_data.emit(row, column, red, green, blue, notes)   


class SaveThread(QThread):
    s_update = QtCore.pyqtSignal(str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.tableName = None
        self.table = None

    def set(self, tableName, table):
        self.tableName = tableName
        self.table = table

    def run(self):

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        for column in range(self.table.columnCount()):

            for row in range(self.table.rowCount()): 
                cell = self.table.item(row, column)

                if cell:          
                    bg = cell.background()
                    note = cell.toolTip()

                    red, green, blue, _ = bg.color().getRgb()
                    color = f"{red}:{green}:{blue}"

                    rowAndColumn = f"{row}:{column}"

                    cursor.execute(f"SELECT rowAndColumn FROM {self.tableName} WHERE rowAndColumn = ?",
                        (rowAndColumn,))
                    
                    dbRowAndColumn = cursor.fetchone()

                    if dbRowAndColumn == None:       
                        cursor.execute(f"INSERT INTO {self.tableName}(rowAndColumn, notes, color, day, month) VALUES(?, ?, ?, ?, ?);",
                            (rowAndColumn, note, color, column, row) )

                        connect.commit()
                        self.s_update.emit('upd')

                    else:
                        cursor.execute(f"UPDATE {self.tableName} SET notes = ? WHERE rowAndColumn = ?",
                            (note, rowAndColumn))

                        cursor.execute(f"UPDATE {self.tableName} SET color = ? WHERE rowAndColumn = ?", 
                            (color, rowAndColumn))

                        cursor.execute(f"UPDATE {self.tableName} SET day = ? WHERE rowAndColumn = ?", 
                            (column, rowAndColumn))

                        cursor.execute(f"UPDATE {self.tableName} SET month = ? WHERE rowAndColumn = ?", 
                            (row, rowAndColumn))

                        connect.commit()
                        self.s_update.emit('upd')

                else:

                    rowAndColumn = f"{row}:{column}"

                    cursor.execute(f"SELECT rowAndColumn FROM {self.tableName} WHERE rowAndColumn = ?",
                        (rowAndColumn,))
                    
                    dbRowAndColumn = cursor.fetchone()

                    if dbRowAndColumn != None:
                        cursor.execute(f"DELETE FROM {self.tableName} WHERE rowAndColumn = ?",
                        (rowAndColumn,))

        connect.close()
        self.s_update.emit('cls')


class SaveReportThread(QThread):
    s_updPB = QtCore.pyqtSignal(str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.tableName = None
        self.table = None
        self.date = None

    def set(self, tableName, table):
        self.tableName = tableName
        self.table = table

    def run(self):
        def standartSave(nameInDB):
            item = cell.text()
            cursor.execute(f"UPDATE {self.tableName} SET {nameInDB} = ? WHERE date = ?", 
            (item, self.date))

            connect.commit()
            self.s_updPB.emit('upd')

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        for row in range(self.table.rowCount() - 2):
            for column in range(self.table.columnCount()):
                cell = self.table.item(row, column)

                if cell and row > 1:
                    match column:

                        case 0:
                            self.date = cell.text()
                            cursor.execute(f"SELECT date FROM {self.tableName} WHERE date = ?", (self.date,))
                            DBdate = cursor.fetchone()

                            if DBdate == None:       
                                cursor.execute(f"INSERT INTO {self.tableName}(date) VALUES(?);", (self.date,))

                            connect.commit()
                            self.s_updPB.emit('upd')

                        case 2:
                            standartSave('price')

                        case 3:
                            standartSave('sum')

                        case 4:
                            standartSave('rent')

                        case 5:
                            standartSave('guest')

                        case 6:
                            standartSave('avito')

                        case 7:
                            standartSave('expense')

                        case 8:
                            standartSave('indications')

                        case 9:
                            standartSave('income')

        connect.close()
        self.s_updPB.emit('cls')


class ReadReportThread(QThread):
    s_readedData = QtCore.pyqtSignal(int, int, str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.tableName = None
        self.table = None
        self.date = None

    def set(self, tableName, table):
        self.tableName = tableName
        self.table = table

    def run(self):
        def standartRead(nameInDB, row, column):
            cursor.execute(f"SELECT {nameInDB} FROM {self.tableName} WHERE date = ?", (self.date,))
            DBdataTemp = cursor.fetchone()

            if DBdataTemp != (None,):

                DBdata = ""
                for i in DBdataTemp:
                    DBdata += str(i) 

                self.s_readedData.emit(row, column, DBdata)

        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        for row in range(self.table.rowCount()): # add -2 for sum line
            for column in range(self.table.columnCount()):
                cell = self.table.item(row, column)

                if row > 1:
                    match column:

                        case 0: 
                            self.date = cell.text()

                        case 2:
                            standartRead('price', row, column)

                        case 3:
                            standartRead('sum', row, column)

                        case 4:
                            standartRead('rent', row, column)

                        case 5:
                            standartRead('guest', row, column)

                        case 6:
                            standartRead('avito', row, column)

                        case 7:
                            standartRead('expense', row, column)

                        case 8:
                            standartRead('indications', row, column)

                        case 9:
                            standartRead('income', row, column)
                            

class SaveDialog(QDialog, saveDialogUI.Ui_Dialog):
    def __init__(self):
        super(SaveDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Сохранение")

    def setRange(self, range_):
        self.pb_save.setRange(0, range_)

    def add(self):
        self.pb_save.setValue(self.pb_save.value() + 1)


class CreateDialog(QDialog, createDialogUI.Ui_Dialog):
    s_upd = QtCore.pyqtSignal()

    def __init__(self):
        super(CreateDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Создать новую таблицу")

        self.btn_create.clicked.connect(self.emitName)

    def emitName(self):
        connect = sqlite3.connect("d.db")
        cursor = connect.cursor()

        name = self.le_name.text()

        if name != '':
            reportName = '_' + name

            try:
                cursor.execute(f"""CREATE TABLE {name} (
                    rowAndColumn TEXT    UNIQUE,
                    notes        TEXT,
                    color        TEXT,
                    day          INTEGER,
                    month        INTEGER
                    );""")

                cursor.execute(f"""CREATE TABLE {reportName} (
                        date        TEXT    UNIQUE,
                        price       INTEGER,
                        sum         INTEGER,
                        rent        INTEGER,
                        guest       INTEGER,
                        avito       INTEGER,
                        expense     INTEGER,
                        indications TEXT,
                        income      INTEGER                 
                    );""")

                connect.commit()
                connect.close()

                self.s_upd.emit()
                self.close()

            except sqlite3.OperationalError:
                self.alert("Невозможно создать таблицу с эти именем!", 
                    "Возможно, таблица с эти именем уже существет, "+
                    "либо имя содержит недопустимые символы.")

        else:
            self.alert("Вы не ввели имя таблицы!")

    def alert(self, text, infoText):
        msg = QMessageBox(text=text,parent=self)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setInformativeText(infoText)
        msg.setIcon(QMessageBox.Icon.Critical)
        ret = msg.exec()


class EditDialog(QDialog, editDialogUI.Ui_Dialog):
    # row, column, color(r, g, b), note
    s_info = QtCore.pyqtSignal(int, int, int, int, int, str)

    def __init__(self):
        super(EditDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Редактирование")
 
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

                    if self.color != None:
                        red, green, blue, _ = self.color.getRgb()
                    else:
                        red, green, blue = (100,100,150)

                    self.s_info.emit(month -1 ,day -1, red, green, blue, notes)
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


class DeleteDialog(QDialog, deleteDialogUI.Ui_Dialog):
    s_cords = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super(DeleteDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Редактирование")

        self.date_in.setDate(QDate.currentDate())
        self.date_out.setDate(QDate.currentDate())

        self.btn_cancel.clicked.connect(lambda: self.close())
        self.btn_del.clicked.connect(self.delete)

    def delete(self):
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
                    self.s_cords.emit(month -1 ,day -1)
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


class ReportDialog(QDialog, reportDialogUI.Ui_Dialog, QDate):
    def __init__(self):
        super(ReportDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Отчёт")

        self.calTable = None
        self.tableName = None

        self.reportSave = SaveReportThread()
        self.reportSave.s_updPB.connect(self.saveDialog)

        self.saveDialog = SaveDialog()
        
        self.btn_close.clicked.connect(lambda: self.close())
        self.btn_save.clicked.connect(self.save)
        self.btn_toSum.clicked.connect(self.setSumRow)

    def start(self):
        def twirt(row, column):
            print(f"row: {row} column: {column}")

        self.setTable()
        self.insertDates()

        self.reportRead = ReadReportThread()
        self.reportRead.set('_' + self.tableName, self.tw_reportTable)
        self.reportRead.s_readedData.connect(self.write)
        self.reportRead.start()

        self.tw_reportTable.cellChanged.connect(self.calculate)  
        self.tw_reportTable.cellClicked.connect(twirt)

    def setSumRow(self):

        # try to use itemChanged function

        lastRow = self.tw_reportTable.rowCount() + 1 
        self.tw_reportTable.setRowCount(self.tw_reportTable.rowCount() + 2)

        self.write(lastRow, 0, "Сумма:")
        self.tw_reportTable.item(lastRow, 0).setBackground(QtGui.QColor(101,216,124))

        for i in range(10):
            if i != 0:
                self.tw_reportTable.setItem(lastRow, i, QTableWidgetItem())
                self.tw_reportTable.item(lastRow, i).setBackground(QtGui.QColor(101,216,124))

    def set(self, calTable, tableName):
        self.calTable = calTable
        self.tableName = tableName

    def setTable(self):

        def defaultWrite(row, column, text):
            self.tw_reportTable.setItem(row, column, QTableWidgetItem())
            self.tw_reportTable.item(row, column).setText(text)
            self.tw_reportTable.item(row, column).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.tw_reportTable.verticalHeader().setVisible(False)
        self.tw_reportTable.horizontalHeader().setVisible(False)
        self.tw_reportTable.setColumnCount(10)
        self.tw_reportTable.setRowCount(2)

        for i in range(4):
            self.tw_reportTable.setSpan(0, i, 2, 1)

        self.tw_reportTable.setSpan(0, 4, 1, 6)

        names = ('Период аренды','Кол-во суток','Стоимость',
            'Сумма','Оплата','Бронь','Гость','Авито','Расход',
            'Показания','Доход')

        row = 0
        column = 0 
        i = 0

        while column < 10:
            
            if column == 4: 
                defaultWrite(row, column, names[i]) 
                defaultWrite(row + 1, column, names[i + 1])
                row = 1 
                i += 1

            else:
                defaultWrite(row, column, names[i])

            column += 1
            i += 1

    def write(self, row, column, text):
        self.tw_reportTable.setItem(row, column, QTableWidgetItem(str(text)))
        self.tw_reportTable.item(row, column).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    def insertDates(self):

        # fetching dates 
        self.colorVariations = []

        for column in range(self.calTable.columnCount()):

            for row in range(self.calTable.rowCount()): 
                cell = self.calTable.item(row, column)

                if cell:

                    red, green, blue, _ = cell.background().color().getRgb()
                    color = f"{red}:{green}:{blue}"

                    if color != None:
                        self.colorVariations.append(color)
                        self.colorVariations.sort()
                    
                        self.colorVariations = list(dict.fromkeys(self.colorVariations))

        for color in self.colorVariations:
            connect = sqlite3.connect("d.db")
            cursor = connect.cursor()

            cursor.execute(f"""SELECT month FROM {self.tableName} WHERE color = '{color}'""")
            DBmonth = cursor.fetchall()
            DBmonth.sort()

            index = 0
            for item in DBmonth:

                monthTemp = ""
                for i in item:
                    monthTemp += str(i)
                month = int(monthTemp)

                DBmonth[index] = month 
                index += 1

            DBmonth = list(dict.fromkeys(DBmonth))

            dayList = []


            for month in DBmonth:
                cursor.execute(f"""SELECT day FROM {self.tableName} WHERE month = {month} AND color = '{color}'""")
                DBday = cursor.fetchall()

                index = 0
                for item in DBday:

                    dayTemp = ""
                    for i in item:
                        dayTemp += str(i)
                    day = int(dayTemp) + 1

                    DBday[index] = day
                    index += 1

                dayList.append(DBday)

            minDay = dayList[0][0]
            maxDay = dayList[-1][-1]

            minMonth = DBmonth[0] + 1
            maxMonth = DBmonth[-1] + 1

            # insert dates in table

            if self.tw_reportTable.rowCount() - 1 == 1:
                self.tw_reportTable.setRowCount(3)

            else:
                self.tw_reportTable.setRowCount(self.tw_reportTable.rowCount() + 1)

            row = self.tw_reportTable.rowCount() - 1 
            text = f"{minDay}.{minMonth} - {maxDay}.{maxMonth}"

            self.write(row, 0, text)

            # insert days in table

            curYear = QDate().currentDate().year()
            minDate = QDate(curYear, minMonth, minDay)
            maxDate = QDate(curYear, maxMonth, maxDay)
            days = str(maxDate.dayOfYear() - minDate.dayOfYear())

            if days == '0':
                self.write(row, 1, '1')
            else:    
                self.write(row, 1, days)

    def calculate(self, row, column):

        if column == 2:
            if self.tw_reportTable.currentItem():
                entered = self.tw_reportTable.currentItem().text()

                if entered.isdigit():
                    days = self.tw_reportTable.item(row, 1).text()
                    self.write(row, 3, str(int(entered) * int(days)))

    def save(self):
        self.saveDialog.setRange(self.tw_reportTable.rowCount() * self.tw_reportTable.columnCount())
        self.saveDialog.show()

        self.reportSave.set('_' + self.tableName, self.tw_reportTable)
        self.reportSave.start()

    def saveDialog(self, msg):
        if msg == 'upd':
            self.saveDialog.add()
        else:
            self.saveDialog.close()


class MainWindow(QMainWindow, mainUI.Ui_MainWindow, QDialog, QColor):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("BusinessThing")
        self.setTable()

        self.changeMenu = QMenu('сменить таблицу', self)

        self.loadAct = QAction('Загрузить', self)
        self.saveAct = QAction('Сохранить', self)
        self.createAct = QAction('Создать', self)
        self.m_file.addAction(self.createAct)
        self.m_file.addAction(self.saveAct)
        self.m_file.addAction(self.loadAct)

        self.saveAct.triggered.connect(self.save)
        self.loadAct.triggered.connect(self.read)
        self.createAct.triggered.connect(lambda: self.createDialog.show())
        self.fetchTables()

        self.tableName = "DefaultTable"

        self.tw_table.cellDoubleClicked.connect(lambda: self.deleteDialog.show())
        self.tw_table.cellClicked.connect(lambda: self.editDialog.show())

        self.btn_report.clicked.connect(self.report)
        self.btn_notes.clicked.connect(lambda: self.editDialog.show())
        self.btn_del.clicked.connect(lambda: self.deleteDialog.show())
        self.btn_save.clicked.connect(self.save)

        self.editDialog = EditDialog()
        self.editDialog.s_info.connect(self.write)

        self.deleteDialog = DeleteDialog()
        self.deleteDialog.s_cords.connect(self.clear)

        self.readThread = ReadThread()
        self.readThread.s_data.connect(self.write)

        self.saveThread = SaveThread()
        self.saveThread.s_update.connect(self.savingDialog)

        self.createDialog = CreateDialog()
        self.createDialog.s_upd.connect(self.updateTableList)

        self.saveDialog = SaveDialog()
        self.reportDialog = ReportDialog()

        self.read()

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

    def fetchTables(self):

        def makeAct(name, item):
            self.name = QAction(str(item), self)
            self.changeMenu.addAction(self.name)
            self.name.triggered.connect(lambda: tableChange(item))

        def tableChange(name):
            self.tableName = str(name)

            # чистка таблицы
            self.tw_table.setRowCount(0)
            self.tw_table.setColumnCount(0)
            self.setTable()

            self.read()

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

            if '_' in clearItem:
                indexCount += 1

            else:
                makeAct(f"{tableList[indexCount]}Act", tableList[indexCount])
                self.m_file.addMenu(self.changeMenu)
                indexCount += 1

        indexCount = 0

    def updateTableList(self):
        self.changeMenu.clear()
        self.fetchTables()

    def savingDialog(self, msg):
        if msg == 'upd':
            self.saveDialog.add()
        else:
            self.saveDialog.close()

    def save(self):
        self.saveDialog.show()
        self.saveDialog.setRange(self.tw_table.columnCount() * self.tw_table.rowCount())

        self.saveThread.set(self.tableName, self.tw_table)
        self.saveThread.start()
    
    def read(self):
        self.readThread.setTableName(self.tableName)
        self.readThread.start()

    def write(self, row, column, red, green, blue, notes):
        self.tw_table.setItem(row, column, QTableWidgetItem())

        if red != None:
            self.tw_table.item(row, column).setBackground(QtGui.QColor(red,green,blue))

        if notes != None:
            self.tw_table.item(row, column).setToolTip(notes)

    def clear(self, row, column):
        self.tw_table.setItem(row, column, None)

    def report(self):
        self.reportDialog.show()
        self.reportDialog.set(self.tw_table, self.tableName)
        self.reportDialog.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
