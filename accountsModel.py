from PyQt5 import QtSql, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class accountsModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()

        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

        self.sqlColumns = super().columnCount()
        self.extraColumns = ["basis"]

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super(accountsModel, self).columnCount()+len(self.extraColumns)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and index.column() >= self.sqlColumns:
            return self.extraColumns[index.column() - self.sqlColumns]

        return super(accountsModel, self).data(index, role)

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # this is similar to `data`
        if section >= self.sqlColumns and orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            print(section)
            return self.extraColumns[section - self.sqlColumns]

        return super(accountsModel, self).headerData(section, orientation, role)

    def flags(self, index):
        # since 2nd column is virtual, it doesn't make sense for it to be Editable
        # other columns can be Editable (default for QSqlTableModel)
        if index.column() >= self.sqlColumns:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def record(self, index):
        rec = super().record(index)

        for col in self.extraColumns:
            newField = QtSql.QSqlField(col)
            newField.setValue(76)
            rec.append(newField)

        return rec

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

