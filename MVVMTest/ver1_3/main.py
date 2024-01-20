import sys
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
 
# окна
import view.mainUI
import view.reportUI
import view.calendarUI
import view.editDialogUI
import view.saveDialogUI
import view.createDialogUI
import view.deleteDialogUI

# проверка обновлений
import launch

# БД
import sqlite3

#ексель
import reportExport

#облако
import CloudUpload

VERSIONPATH = 'ver1_3'


class ReadThread(QThread):
    # row, column, color(r, g, b), note
    s_data = QtCore.pyqtSignal(int, int, int, int, int, str)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.tableName = None

    def setTableName(self, tableName):
        self.tableName = tableName

    def run(self):

        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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

        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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

        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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

            if DBdataTemp != (None,) and DBdataTemp != None:
                DBdata = ""
                for i in DBdataTemp:
                    DBdata += str(i) 

                self.s_readedData.emit(row, column, DBdata)

        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
        cursor = connect.cursor()

        for row in range(self.table.rowCount() - 2):
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
   

class SumReportThread(QThread):
    s_sumData = QtCore.pyqtSignal(int)

    def  __init__(self):
        QtCore.QThread.__init__(self)

        self.table = None
        self.columnList = [4, 5, 6, 9]

    def set(self, table):
        self.table = table

    def run(self):

        for column in self.columnList:

            total = 0
            row = self.table.rowCount() - 2

            for row in range(row):
                if row != 0:
                    item = self.table.item(row, column)
                    if item and item.text().isdigit():
                        total += int(item.text())

            self.s_sumData.emit(total)        


class SaveDialog(QDialog, view.saveDialogUI.Ui_Dialog, QSize):
    def __init__(self):
        super(SaveDialog, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(f'{VERSIONPATH}/assets/icon96px.ico'))
        self.setWindowTitle("Сохранение")
        self.setFixedSize(QSize(400, 84))

    def setRange(self, range_):
        self.pb_save.setRange(0, range_)

    def add(self):
        self.pb_save.setValue(self.pb_save.value() + 1)


class CreateDialog(QDialog, view.createDialogUI.Ui_Dialog, QSize):
    s_upd = QtCore.pyqtSignal()

    def __init__(self):
        super(CreateDialog, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(f'{VERSIONPATH}/icon96px.ico'))
        self.setWindowTitle("Создать новую таблицу")
        self.setFixedSize(QSize(350, 110))

        self.btn_create.clicked.connect(self.emitName)

    def emitName(self):
        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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


class EditDialog(QDialog, view.editDialogUI.Ui_Dialog, QSize):
    # row, column, color(r, g, b), note
    s_info = QtCore.pyqtSignal(int, int, int, int, int, str)

    def __init__(self):
        super(EditDialog, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(f'{VERSIONPATH}/icon96px.ico'))
        self.setWindowTitle("Редактирование")
        self.setFixedSize(QSize(370, 430))
 
        self.date_in.setDate(QDate.currentDate())
        self.date_out.setDate(QDate.currentDate())

        self.btn_color.clicked.connect(self.colorDialog)
        self.btn_save.clicked.connect(self.save)
        
        self.color = None
        self.notes = None
        
    def setStyle(self, style):
        self.setStyleSheet(style)

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


class DeleteDialog(QDialog, view.deleteDialogUI.Ui_Dialog, QSize):
    s_cords = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super(DeleteDialog, self).__init__()
        self.setupUi(self)

        self.setWindowIcon(QtGui.QIcon(f'{VERSIONPATH}/icon96px.ico'))
        self.setWindowTitle("Редактирование")
        self.setFixedSize(QSize(302, 170))

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

        while True:

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
                break

    def setStyle(self, styleSheet):
        self.setStyleSheet(styleSheet)
    
    
class ReportPage(QMainWindow, view.reportUI.Ui_MainWindow, QDate):
    def __init__(self):
        super(ReportPage, self).__init__()
        self.setupUi(self)
        
        self.path = None
        self.calTable = None
        self.tableName = None
        self.totalList = []
        
        self.btn_save.clicked.connect(self.save)
        self.btn_export.clicked.connect(self.export) 

        self.reportSave = SaveReportThread()
        self.reportSave.s_updPB.connect(self.saveDialog)

        self.reportSum = SumReportThread()
        self.reportSum.s_sumData.connect(self.changeSumRow)
        
        self.reportExport = reportExport

        self.saveDialog = SaveDialog()
        
    def start(self):

        self.setTable()
        self.insertDates() 
        self.setSumRow()

        self.reportRead = ReadReportThread()
        self.reportRead.set('_' + self.tableName, self.tw_reportTable)
        self.reportRead.finished.connect(lambda: self.reportSum.start())
        self.reportRead.s_readedData.connect(self.write)
        self.reportRead.start()

        self.reportSum.set(self.tw_reportTable)
        self.tw_reportTable.cellChanged.connect(self.calculate) 

    def changeSumRow(self, total):

        lastRow = self.tw_reportTable.rowCount() - 1
        aligment = QtCore.Qt.AlignmentFlag.AlignCenter

        self.totalList.append(total)

        if len(self.totalList) == 4 :
            column = 4
            for item in self.totalList:
                cell = self.tw_reportTable.item(lastRow, column)
                cell.setText(str(item))  
                cell.setTextAlignment(aligment)

                if column < 6:
                    column += 1
                else:
                    column = 9

            self.totalList.clear()

    def set(self, calTable, tableName):
        self.calTable = calTable
        self.tableName = tableName
        
    def color(self, row, column):

        colors = ((191,255,172), (255,219,224), (249,211,249), 
            (249,211,249), (243,243,155), (255,237,178), 
            (202,199,248))

        match column:

            case 4:
                if row == 0:
                    red, green, blue = colors[0]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

                else:
                    red, green, blue = colors[1]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

            case 5:
                    red, green, blue = colors[2]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

            case 6:
                    red, green, blue = colors[3]
                    cell = self.tw_reportTable.item(row, column)
                    
                    cell.setBackground(QtGui.QColor(red, green, blue))

            case 7:
                    red, green, blue = colors[4]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

            case 8:
                    red, green, blue = colors[5]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

            case 9:
                    red, green, blue = colors[6]
                    cell = self.tw_reportTable.item(row, column)
                    cell.setBackground(QtGui.QColor(red, green, blue))

    def write(self, row, column, text):
        aligment = QtCore.Qt.AlignmentFlag.AlignCenter
        self.tw_reportTable.setItem(row, column, QTableWidgetItem())
        self.tw_reportTable.item(row, column).setText(text)
        self.tw_reportTable.item(row, column).setTextAlignment(aligment)

        self.color(row, column)

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
            connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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

            minDay = dayList[0][0]   #FIX: IndexError: list index out of range
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
            entered = self.tw_reportTable.currentItem()

            if entered and entered.text().isdigit():
                days = self.tw_reportTable.item(row, 1).text()
                self.write(row, 3, str(int(entered.text()) * int(days)))

        elif column == 4 or 5 or 6 or 9:
            self.reportSum.start()

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
            
    def exportDialog(self):
        self.path = QFileDialog.getUrl()

    def export(self):
        msg = self.reportExport.export(self.tw_reportTable)
        if msg:
            self.animations.PopUpAnimation()
        

class CalendarPage(QMainWindow, view.calendarUI.Ui_MainWindow, QDialog, QColor, QSize, QSizePolicy, QHeaderView, QGridLayout):
    s_saveFinished = QtCore.pyqtSignal(bool)
    
    def __init__(self):
        super(CalendarPage, self).__init__()
        self.setupUi(self)
        
        self.tableName = "DefaultTable"
        self.reportOpenAllow = False
        
        self.tw_table.cellDoubleClicked.connect(lambda: self.deleteDialog.show())
        self.tw_table.cellClicked.connect(lambda: self.editDialog.show())
        self.btn_notes.clicked.connect(lambda: self.editDialog.show())
        self.btn_del.clicked.connect(lambda: self.deleteDialog.show())
        self.btn_save.clicked.connect(self.save)
        
        self.readThread = ReadThread()
        self.readThread.s_data.connect(self.write)

        self.saveThread = SaveThread()
        self.saveThread.s_update.connect(self.savingDialog)
        self.saveThread.finished.connect(lambda: self.s_saveFinished.emit(True))

        self.editDialog = EditDialog()
        self.editDialog.s_info.connect(self.write)

        self.deleteDialog = DeleteDialog()
        self.deleteDialog.s_cords.connect(self.clear)
        
        self.saveDialog = SaveDialog()

        self.setTable()
        self.read()
        
    def resizeable(self):
    
        verLayout = QVBoxLayout()
        horLayout = QHBoxLayout()
        
        btnList = [self.btn_del, self.btn_notes, self.btn_save]

        for button in btnList:
            horLayout.addWidget(button)
            button.setMinimumSize(QSize(130, 30))

        horLayout.insertStretch(1, 500)
        
        verLayout.addWidget(self.tw_table)
        sizePolicy = QtWidgets.QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.tw_table.setSizePolicy(sizePolicy)

        verLayout.addLayout(horLayout)
        self.centralwidget.setLayout(verLayout)
        
    def setStyle(self, style):
        self.editDialog.setStyleSheet(style)
        self.deleteDialog.setStyleSheet(style)
        self.saveDialog.setStyleSheet(style)
        
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

        verHeader = self.tw_table.verticalHeader()
        horHeader = self.tw_table.horizontalHeader()

        for i in range(self.tw_table.rowCount()):
            verHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        for i in range(self.tw_table.columnCount()):
            horHeader.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # verHeader.setDefaultAlignment(QtCore.Qt.AlignCenter) #TODO: Fix that
        # horHeader.setDefaultAlignment(QtCore.Qt.AlignCenter) #TODO: n' that

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

        
class MainWindow(QMainWindow, view.mainUI.Ui_MainWindow, QDialog, QColor, QSize, QSizePolicy, QHeaderView, QGridLayout):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)        
        self.setWindowIcon(QtGui.QIcon(f'{VERSIONPATH}/assets/icon96px.ico'))
        self.setWindowTitle("BusinessThing")
        self.statusbar.showMessage("ver 1.3")
        self.resizeable()
        self.setActions()
        self.fetchTables()
        
        self.deleteDialog = DeleteDialog()
        self.saveDialog = SaveDialog()
        self.editDialog = EditDialog()
        
        self.createDialog = CreateDialog()
        self.createDialog.s_upd.connect(self.updateTableList)
        
        self.calendarPage = CalendarPage()
        self.calendarPage.s_saveFinished.connect(self.reportOpen)
        self.calendarPage.resizeable()
        
        self.reportPage = ReportPage()
        self.reportPage.resizeable()
        
        self.theme = "Light"
        self.reportOpenAllow = False
        self.setTabBar(self.tb_main)
        self.setTheme()
        
    def setTabBar(self, tabBar):
        tabBar.addTab(self.calendarPage, "Календарь")
        tabBar.addTab(self.reportPage, "Отчёт")

        tabBar.setTabIcon(0, QIcon("assets/left-dark-arrow-50.png")) # placeholder
        tabBar.setTabIcon(1, QIcon("assets/right-dark-arrow-50.png")) # placeholder
        tabBar.tabBarClicked.connect(self.report)
        tabBar.setCurrentIndex(2)

    def setActions(self):
        self.changeMenu = QMenu('сменить таблицу', self)

        self.loadAct = QAction('Загрузить', self)
        self.saveAct = QAction('Сохранить', self)
        self.createAct = QAction('Создать', self)
        self.uploadAct = QAction('Сохранить в облаке', self)
        self.m_file.addAction(self.createAct)
        self.m_file.addAction(self.saveAct)
        self.m_file.addAction(self.loadAct)
        self.m_file.addAction(self.uploadAct)

        self.themeAct = QAction('Сменить тему', self)
        self.m_settings.addAction(self.themeAct)

        self.themeAct.triggered.connect(self.setTheme)
        self.saveAct.triggered.connect(self.pageSave)
        self.loadAct.triggered.connect(self.pageRead)
        self.uploadAct.triggered.connect(lambda: CloudUpload.upload())
        self.createAct.triggered.connect(lambda: self.createDialog.show())

    def setTheme(self):
        if self.theme == "Light":
            with open('ver1_3/themes/lightDefault/main.css') as file:
                style = file.read()
                self.setStyleSheet(style)
                
            with open('ver1_3/themes/lightDefault/report.css') as file:
                style = file.read()
                self.reportPage.setStyleSheet(style)
                
            with open('ver1_3/themes/lightDefault/calendar.css') as file:
                style = file.read()
                self.calendarPage.setStyleSheet(style)
        
            with open('ver1_3/themes/lightDefault/std.css') as file: 
                style = file.read()
                self.createDialog.setStyleSheet(style)
                self.calendarPage.setStyle(style)

            self.theme = "Dark"

        else:
            with open('ver1_3/themes/darkDefault/main.css') as file:
                style = file.read()
                self.setStyleSheet(style)
                
            with open('ver1_3/themes/darkDefault/report.css') as file:
                style = file.read()
                self.reportPage.setStyleSheet(style)
                
            with open('ver1_3/themes/darkDefault/calendar.css') as file:
                style = file.read()
                self.calendarPage.setStyleSheet(style)
                
            with open('ver1_3/themes/darkDefault/std.css') as file: 
                style = file.read()
                self.createDialog.setStyleSheet(style)
                self.calendarPage.setStyle(style)

            self.theme = "Light"

    def resizeable(self):
        sizePolicy = QtWidgets.QSizePolicy(QSizePolicy.Policy.Expanding, 
                                           QSizePolicy.Policy.Expanding)
        self.tb_main.setSizePolicy(sizePolicy)
        self.setCentralWidget(self.tb_main)
    
    def pageSave(self):
        page = self.sw_main.currentIndex()
        if page == 0:
             self.calendarPage.save()
                    
        else:
            self.reportPage.save()
                
    def pageRead(self):
        page = self.sw_main.currentIndex()
        if page == 0:
            self.calendarPage.read()
                
        else:
            self.reportPage.read()                        
        
    def fetchTables(self):

        def makeAct(name, item):
            self.name = QAction(str(item), self)
            self.changeMenu.addAction(self.name)
            self.name.triggered.connect(lambda: tableChange(item))

        def tableChange(name):
            self.calendarPage.tableName = str(name)

            # сброс таблицы
            self.calendarPage.tw_table.setRowCount(0)
            self.calendarPage.tw_table.setColumnCount(0)
            self.calendarPage.setTable()

            self.calendarPage.read()

        connect = sqlite3.connect(f"{VERSIONPATH}/database/d.db")
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

    def report(self): 
        if self.tb_main.currentIndex() == 0:
            self.calendarPage.save()
            self.reportOpenAllow = True

    def reportOpen(self, saveFinished):
        calendar = self.calendarPage
        report = self.reportPage
        
        if self.reportOpenAllow and saveFinished:
            report.set(calendar.tw_table, calendar.tableName)
            report.start()
            self.reportOpenAllow = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()
    sys.exit(app.exec())
    
