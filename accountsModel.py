from PyQt5 import QtSql, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

class accountsModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()
        
        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return super(accountsModel, self).columnCount()+1


    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole and index.column()==7:
            return "Hello"
        return super(accountsModel, self).data(index, role)


    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        # this is similar to `data`
        if section==7 and orientation==QtCore.Qt.Horizontal and role==QtCore.Qt.DisplayRole:
            return 'basis'
        return super(accountsModel, self).headerData(section, orientation, role)


    def flags(self, index):
        # since 2nd column is virtual, it doesn't make sense for it to be Editable
        # other columns can be Editable (default for QSqlTableModel)
        if index.column()==7:
            return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled
        return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable

    def record(self, index):
        rec = super().record(index)
        basisField = QtSql.QSqlField("basis")
        basisField.setValue(76)
        rec.append(basisField)

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

