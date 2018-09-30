import csv
import urllib.request
import codecs
from datetime import datetime

from PyQt5 import QtSql, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from financial import financial

class accountsModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()

        self.cache = {"folionum": None}
        self.transactionModel = transactionModel()

        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

        self.sqlColumns = super().columnCount()
        self.headerList = [
            "basis", "currentnav", "balanceunits", "currentvalue",
            "realisedprofits", "unrealisedprofits", "totalprofits",
            "xirr",
        ]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super(accountsModel, self).columnCount()+len(self.extraColumns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and index.column() >= self.sqlColumns:
            header = self.headerList[index.column() - self.sqlColumns]
            self.calculateExtraColumns(index.row())
            return self.cache[header]

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

    def record(self, rowIndex):
        rec = super().record(rowIndex)

        self.calculateExtraColumns(rowIndex)
        for col in self.headerList:
            newField = QtSql.QSqlField(col)
            newField.setValue(self.cache[col])
            rec.append(newField)

        return rec

    @pyqtSlot()
    def updateNAV(self):
        url = 'https://www.amfiindia.com/spages/NAVAll.txt'
        response = urllib.request.urlopen(url)
        cr = csv.DictReader(codecs.iterdecode(response, 'utf-8'), delimiter=";")

        QtSql.QSqlDatabase.database().transaction()
        q = QtSql.QSqlQuery();
        q.prepare("delete from currentnav")
        if not q.exec():
            raise Exception(q.lastError().text())

        q.prepare("insert into currentnav values(:schemecode, :isin, :isin_div_reinv, :schemename, :nav, :date)")
        for row in cr:
            if row["Net Asset Value"] is not None:
                q.bindValue(":schemecode", row["Scheme Code"])
                q.bindValue(":isin", row["ISIN Div Payout/ ISIN Growth"])
                q.bindValue(":isin_div_reinv", row["ISIN Div Reinvestment"])
                q.bindValue(":schemename", row["Scheme Name"])
                q.bindValue(":nav", row["Net Asset Value"])
                q.bindValue(":date", row["Date"])
                if not q.exec():
                    raise Exception(q.lastError().text())
        QtSql.QSqlDatabase.database().commit()

    def calculateExtraColumns(self, rowIndex):
        folio = super().record(rowIndex).value("folionum")
        if self.cache["folionum"] == folio:
            return

        self.cache["folionum"] = folio
        self.transactionModel.setFilter("folionum='" + folio + "'")
        self.transactionModel.setSort(self.transactionModel.fieldIndex("trandate"), QtCore.Qt.AscendingOrder)
        self.transactionModel.select()

        cashflows = []
        remTrans = []
        self.cache["realisedprofits"] = 0
        for row in range(self.transactionModel.rowCount()):
            record = self.transactionModel.record(row)

            tranType = record.value("trantype")
            units = record.value("tranunits")
            rate = record.value("tranrate")
            amount = record.value("tranamt")
            date = datetime.strptime(record.value("trandate"), "%Y-%m-%d")

            if (tranType == "Purchase") or (tranType == "Dividend" and units != ""):
                remTrans.append({"units": units, "rate": rate})
                cashflows.append((date, -amount))
            elif (tranType == "Redemption") or (tranType == "ProfitB"):
                cashflows.append((date, amount))
                while (units > 0) and len(remTrans) > 0:
                    if (units >= remTrans[-1]["units"]):
                        units = units - remTrans[-1]["units"]
                        self.cache["realisedprofits"] = self.cache["realisedprofits"] + remTrans[-1]["units"] * (rate - remTrans[-1]["rate"])
                        remTrans.pop()
                    else:
                        remTrans[-1]["units"] = remTrans[-1]["units"] - units
                        self.cache["realisedprofits"] = self.cache["realisedprofits"] + units * (rate - remTrans[-1]["rate"])
                        units = 0
        
        self.cache["basis"] = 0
        self.cache["balanceunits"] = 0
        for t in remTrans:
            self.cache["basis"] = self.cache["basis"] + t["units"] * t["rate"]
            self.cache["balanceunits"] = self.cache["balanceunits"] + t["units"]
        
        foliocode = super().record(rowIndex).value("foliocode")
        self.cache["currentnav"] = self.getCurrentNAV(foliocode)

        if self.cache["currentnav"] is not None:
            self.cache["currentvalue"] = self.cache["balanceunits"] * self.cache["currentnav"]
            self.cache["unrealisedprofits"] = self.cache["currentvalue"] - self.cache["basis"]
            self.cache["totalprofits"] = self.cache["realisedprofits"] + self.cache["unrealisedprofits"]
            
            cashflows.append((datetime.now(), self.cache["currentvalue"]))
            self.cache["xirr"] = financial.xirr(cashflows)
        else:
            self.cache["currentvalue"] = 0
            self.cache["unrealisedprofits"] = 0
            self.cache["totalprofits"] = 0
            self.cache["xirr"] = 0

    def getCurrentNAV(self, code):
        q = QtSql.QSqlQuery()
        q.prepare("select nav from currentnav where schemecode == ?")
        q.bindValue(0, code)
        if not q.exec():
            raise Exception(q.lastError().text())
        q.next()
        nav = q.value(0)
        
        return nav

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

