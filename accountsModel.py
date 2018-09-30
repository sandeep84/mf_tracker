import csv
import urllib.request
import codecs

from PyQt5 import QtSql, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from collections import OrderedDict

class accountsModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()

        self.cache = {"folionum": None}
        self.transactionModel = transactionModel()

        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

        self.sqlColumns = super().columnCount()
        self.extraColumns = OrderedDict([
            ("basis", self.calculateBasis),
            ("currentnav", self.currentNAV),
        ])
        self.headerList = list(self.extraColumns.keys())

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super(accountsModel, self).columnCount()+len(self.extraColumns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and index.column() >= self.sqlColumns:
            header = self.headerList[index.column() - self.sqlColumns]
            return self.extraColumns[header](index.row())

        return super(accountsModel, self).data(index, role)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # this is similar to `data`
        if section >= self.sqlColumns and orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            return self.headerList[section - self.sqlColumns]

        return super(accountsModel, self).headerData(section, orientation, role)

    def flags(self, index):
        # since 2nd column is virtual, it doesn't make sense for it to be Editable
        # other columns can be Editable (default for QSqlTableModel)
        if index.column() >= self.sqlColumns:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def record(self, index):
        rec = super().record(index)

        for col in self.headerList:
            newField = QtSql.QSqlField(col)
            newField.setValue(self.extraColumns[col](index))
            rec.append(newField)

        return rec

    @pyqtSlot()
    def updateNAV(self):
        url = 'https://www.amfiindia.com/spages/NAVAll.txt'
        response = urllib.request.urlopen(url)
        cr = csv.DictReader(codecs.iterdecode(response, 'utf-8'), delimiter=";")

        # QSqlQuery q;
        # q.prepare("insert into currentnav values(?, ?, ?, ?, ?, ?)")

        for row in cr:
            print (row)

    def calculateExtraColumns(self, rowIndex):
        folio = super().record(rowIndex).value("folionum")
        if self.cache["folionum"] == folio:
            return

        self.transactionModel.setFilter("folionum='" + folio + "'")
        self.transactionModel.setSort(self.transactionModel.fieldIndex("trandate"), QtCore.Qt.AscendingOrder)
        self.transactionModel.select()

        remTrans = []
        for row in range(self.transactionModel.rowCount()):
            record = self.transactionModel.record(row)

            tranType = record.value("trantype")
            units = record.value("tranunits")
            rate = record.value("tranrate")

            if (tranType == "Purchase"):
                remTrans.append({"units": units, "rate": rate})
            elif (tranType == "Redemption") or (tranType == "ProfitB"):
                while (units > 0) and len(remTrans) > 0:
                    if (units >= remTrans[-1]["units"]):
                        units = units - remTrans[-1]["units"]
                        remTrans.pop()
                    else:
                        remTrans[-1]["units"] = remTrans[-1]["units"] - units
                        units = 0
        
        basis = 0
        for t in remTrans:
            basis = basis + t["units"] * t["rate"]
        
        self.cache["basis"] = "{0:.2f}".format(basis)

    def calculateBasis(self, index):
        self.calculateExtraColumns(index)
        return self.cache["basis"]

    def currentNAV(self, index):
        folio = super().record(index).value("folionum")
        return 10


class transactionModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()
        self.folioFilter = ""
        
        self.setTable('transactions') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()
        self.removeColumn(0)

    @pyqtSlot(str)
    def updateFolioFilter(self, folio):
        self.folioFilter = "folionum='" + folio + "'"
        self.setFilter(self.folioFilter)

