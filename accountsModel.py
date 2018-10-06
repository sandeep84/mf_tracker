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

        self.cache = {"Folio Number": None}
        self.transactionModel = transactionModel()

        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

        self.sqlColumns = super().columnCount()
        self.headerList = [
            "Basis", "Current NAV", "Balance Units", "Current Value",
            "Realised Profits", "Unrealised Profits", "Total Profits",
            "XIRR",
        ]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super(accountsModel, self).columnCount()+len(self.headerList)

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

    def updateFolioNum(self, rowIndex, folioNum):
        idx = self.createIndex(rowIndex, self.fieldIndex("Folio Number"))
        QtSql.QSqlDatabase.database().transaction()
        q = QtSql.QSqlQuery();
        q.prepare("update transactions set `Folio Number`=:newFolio where `Folio Number`=:oldFolio")
        q.bindValue(":oldFolio", self.cache["Folio Number"])
        q.bindValue(":newFolio", folioNum)
        if not q.exec():
            raise Exception(q.lastError().text())
        QtSql.QSqlDatabase.database().commit()
        self.setData(idx, folioNum)
        self.cache["Folio Number"] = folioNum

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
        folio = super().record(rowIndex).value("Folio Number")
        if self.cache["Folio Number"] == folio:
            return

        self.cache["Folio Number"] = folio
        self.transactionModel.updateFolioFilter(folio)
        self.transactionModel.setSort(self.transactionModel.fieldIndex("Date"), QtCore.Qt.AscendingOrder)
        self.transactionModel.select()

        cashflows = []
        remTrans = []
        self.cache["Realised Profits"] = 0
        for row in range(self.transactionModel.rowCount()):
            record = self.transactionModel.record(row)

            tranType = record.value("Type")
            units = record.value("Units")
            rate = record.value("Rate")
            amount = record.value("Amount")
            date = datetime.strptime(record.value("Date"), "%Y-%m-%d")

            if (tranType == "Purchase"):
                remTrans.append({"units": units, "rate": rate})
                cashflows.append((date, -amount))
            elif (tranType == "Dividend" and units == ""):
                self.cache["Realised Profits"] = self.cache["Realised Profits"] + amount
            elif (tranType == "Dividend" and units != ""):
                # Dividend reinvestment
                # Does not affect basis, only affects current value
                #  - force rate, amount to 0
                remTrans.append({"units": units, "rate": 0.00})
                cashflows.append((date, 0.00))
            elif (tranType == "Redemption") or (tranType == "ProfitB"):
                cashflows.append((date, amount))
                while (units > 0) and len(remTrans) > 0:
                    if (units >= remTrans[-1]["units"]):
                        units = units - remTrans[-1]["units"]
                        self.cache["Realised Profits"] = self.cache["Realised Profits"] + remTrans[-1]["units"] * (rate - remTrans[-1]["rate"])
                        remTrans.pop()
                    else:
                        remTrans[-1]["units"] = remTrans[-1]["units"] - units
                        self.cache["Realised Profits"] = self.cache["Realised Profits"] + units * (rate - remTrans[-1]["rate"])
                        units = 0
        
        self.cache["Basis"] = 0
        self.cache["Balance Units"] = 0
        for t in remTrans:
            self.cache["Basis"] = self.cache["Basis"] + t["units"] * t["rate"]
            self.cache["Balance Units"] = self.cache["Balance Units"] + t["units"]
        
        foliocode = super().record(rowIndex).value("Scheme Code")
        self.cache["Current NAV"] = self.getCurrentNAV(foliocode)

        if self.cache["Current NAV"] is not None:
            self.cache["Current Value"] = self.cache["Balance Units"] * self.cache["Current NAV"]
            self.cache["Unrealised Profits"] = self.cache["Current Value"] - self.cache["Basis"]
            self.cache["Total Profits"] = self.cache["Realised Profits"] + self.cache["Unrealised Profits"]
            
            cashflows.append((datetime.now(), self.cache["Current Value"]))
            self.cache["XIRR"] = financial.xirr(cashflows)
        else:
            self.cache["Current Value"] = 0
            self.cache["Unrealised Profits"] = 0
            self.cache["Total Profits"] = 0
            self.cache["XIRR"] = 0

    def getCurrentNAV(self, code):
        nav = None

        q = QtSql.QSqlQuery()
        q.prepare("select nav from currentnav where schemecode == ?")
        q.bindValue(0, code)
        if not q.exec():
            raise Exception(q.lastError().text())
        if q.next():
            nav = q.value(0)
        
        return nav

class transactionModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()
        self.folioFilter = ""
        
        self.setTable('transactions') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    @pyqtSlot(str)
    def updateFolioFilter(self, folio):
        self.folioFilter = "`Folio Number`='" + folio + "'"
        self.setFilter(self.folioFilter)

