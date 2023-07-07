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
import sqlite3


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

        for index in range(count):
            if index != 0:

                # row, column
                cursor.execute(f"SELECT rowAndColumn FROM {self.tableName} WHERE ROWID = ?", (index,))
                rowAndColumnTemp = cursor.fetchone()

                if rowAndColumnTemp != (None,):

                    rowAndColumn = ""
                    for i in rowAndColumnTemp:
                        rowAndColumn += str(i)

                    rowAndColumn = rowAndColumn.split(":")
                    row = int(rowAndColumn[0])
                    column = int(rowAndColumn[1])

                    # notes
                    cursor.execute(f"SELECT notes FROM {self.tableName} WHERE ROWID = ?", (index,))
                    notesTemp = cursor.fetchone()

                    if notesTemp != (None,):

                        notes = ""
                        for i in notesTemp:
                            notes += str(i)

                    else:
                        notes = None

                    # color
                    cursor.execute(f"SELECT color FROM {self.tableName} WHERE ROWID = ?", (index,))
                    colorTemp = cursor.fetchone()

                    if colorTemp != (None,):

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

    def setTableName(self, tableName):
        self.tableName = tableName

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

                    cursor.execute(f"SELECT rowAndColumn FROM {self.tableName} WHERE rowAndColumn = ?",
                        (rowAndColumn,))
                    
                    dbRowAndColumn = cursor.fetchone()

                    if dbRowAndColumn is None:       
                        cursor.execute(f"INSERT INTO {self.tableName}(rowAndColumn, notes, color) VALUES(?, ?, ?);",
                            (rowAndColumn, note, color) )

                        self.s_update.emit('upd')

                    else:
                        cursor.execute(f"UPDATE {self.tableName} SET notes = ? WHERE rowAndColumn = ?",
                            (note, rowAndColumn))

                        cursor.execute(f"UPDATE {self.tableName} SET color = ? WHERE rowAndColumn = ?", 
                            (color, rowAndColumn))

                        self.s_update.emit('upd')
                    
                    connect.commit()

                else:

                    rowAndColumn = f"{row}:{column}"

                    cursor.execute(f"SELECT rowAndColumn FROM {self.tableName} WHERE rowAndColumn = ?",
                        (rowAndColumn,))
                    
                    dbRowAndColumn = cursor.fetchone()

                    if dbRowAndColumn is None:       
                        cursor.execute(f"INSERT INTO {self.tableName}(rowAndColumn, notes, color) VALUES(?, ?, ?);",
                            (rowAndColumn, None, None) )

                        self.s_update.emit('upd')

                    else:
                        cursor.execute(f"UPDATE {self.tableName} SET notes = ? WHERE rowAndColumn = ?",
                            (None, rowAndColumn))

                        cursor.execute(f"UPDATE {self.tableName} SET color = ? WHERE rowAndColumn = ?", 
                            (None, rowAndColumn))

                        self.s_update.emit('upd')
                    
                    connect.commit()

        connect.close()
        self.s_update.emit('cls')


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
            try:
                cursor.execute(f"""CREATE TABLE {name} (
                    rowAndColumn TEXT UNIQUE,
                    notes        TEXT,
                    color        TEXT
                    );""")

                connect.commit()
                connect.close()

                self.s_upd.emit()
                self.close()

            except sqlite3.OperationalError:
                self.alert("Данная таблица уже существует!")

        else:
            self.alert("Вы не ввели имя таблицы!")

    def alert(self, text):
        msg = QMessageBox(text=text,parent=self)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
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


class ReportDialog(QDialog, reportDialogUI.Ui_Dialog):
    def __init__(self):
        super(ReportDialog, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("Отчёт")

        self.calTable = None

        self.btn_close.clicked.connect(lambda: self.close())

        self.setTable()

    def setCalTable(self, table):
        self.calTable = table

    def setTable(self):
        #self.tw_reportTable.setColumnCount(11)
        self.tw_reportTable.setRowCount(2)
        self.tw_reportTable.setSpan(0, 4, 1, 6)

        HeaderTyple = (
            'Период аренды', 'Кол-во суток','Стоимость',
            'Сумма','Оплата'
            )
        
        self.tw_reportTable.setHorizontalHeaderLabels(HeaderTyple)


class MainWindow(QMainWindow, mainUI.Ui_MainWindow, QDialog, QColor):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.setWindowTitle("BusinessThing")
        self.setTable()

        menubar = self.menuBar()
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

        self.btn_report.clicked.connect(lambda: self.reportDialog.show())
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
            makeAct(f"{tableList[indexCount]}Act", tableList[indexCount])

            self.m_file.addMenu(self.changeMenu)
            indexCount += 1

        indexCount = 0

    def updateTableList(self):
        self.changeMenu.clear()
        self.fetchTables()

    def save(self):
        self.saveDialog.show()
        self.saveDialog.setRange(self.tw_table.columnCount() * self.tw_table.rowCount())

        self.saveThread.setTableName(self.tableName)
        self.saveThread.setTable(self.tw_table)
        self.saveThread.start()

    def savingDialog(self, msg):
        if msg == 'upd':
            self.saveDialog.add()
        else:
            self.saveDialog.close()
    
    def read(self):
        self.readThread.setTableName(self.tableName)
        self.readThread.start()

    def write(self, row, column, red, green, blue, notes):
        self.tw_table.setItem(row, column, QTableWidgetItem())

        if red or green or blue != None:
            self.tw_table.item(row, column).setBackground(QtGui.QColor(red,green,blue))

        if notes != None:
            self.tw_table.item(row, column).setToolTip(notes)

    def clear(self, row, column):

        self.tw_table.setItem(row, column, None)
        
    """
    Report table

    def cleaningForReport(self):
        self.tw_table.setColumnCount(0)
        self.tw_table.setRowCount(0)
        self.tw_table.setSpan(0, 4, 1, 6)

        self.setTableReport()


    def setTableReport(self):
        self.tw_table.setColumnCount(11)
        self.tw_table.setRowCount(2)

        HeaderTyple = (
            'Период аренды', 'Кол-во суток','Стоимость',
            'Сумма','Оплата'
            )
        
        self.tw_table.setHorizontalHeaderLabels(HeaderTyple)
    """

if __name__ == '__main__':
    app = QApplication(sys.argv)
    m = MainWindow()
    m.show()    
    sys.exit(app.exec())
