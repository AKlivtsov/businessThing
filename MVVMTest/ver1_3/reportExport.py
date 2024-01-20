import pandas
from PyQt6.QtWidgets import QTableWidget

def export(tw_reportTable: QTableWidget) -> str:
        data = {}
        columnName = []

        for column in range(tw_reportTable.columnCount()):
            item = tw_reportTable.item(0, column)
            if item is not None:
                if item.text() != "Оплата":
                    columnName.append(item.text())
                else:
                    for column in range(1, tw_reportTable.columnCount()):
                        item = tw_reportTable.item(1, column)
                        if item is not None:
                            columnName.append(item.text())

        for column in columnName:
            rowList = []
            for row in range(2, tw_reportTable.rowCount()):

                item = tw_reportTable.item(row, columnName.index(column))
                if item is not None:
                    rowList.append(item.text())
                else:
                    rowList.append('')

            for item in rowList:
                data[column] = rowList

        df = pandas.DataFrame.from_dict(data, orient='index')
        df = df.transpose()
        df.to_excel('./export.xlsx')
        
        return "table exported successfully"
