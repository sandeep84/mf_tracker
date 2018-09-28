import sys

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSlot, QObject, QByteArray, QVariant, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlApplicationEngine
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QApplication
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQuick import QQuickView


class QtTabModel(QSqlTableModel):
    def __init__(self, db):
        super(QtTabModel, self).__init__(db=db)

    def roleNames(self):
        roles = {}
        for i in range(self.columnCount()):
            roles[Qt.UserRole + i + 1] = QByteArray(self.headerData(i, Qt.Horizontal).encode('utf-8'))

        return roles

    def data(self, index, role):
        if role < Qt.UserRole:
            # caller requests non-UserRole data, just pass to papa
            return super(QtTabModel, self).data(index, role)

        # caller requests UserRole data, convert role to column (role - Qt.UserRole -1) to return correct data
        return super(QtTabModel, self).data(self.index(index.row(), role - Qt.UserRole -1), Qt.DisplayRole)

    @pyqtSlot(result=QVariant)  # don't know how to return a python array/list, so just use QVariant
    def roleNameArray(self):
        # This method is used to return a list that QML understands
        list = []
        # list = self.roleNames().items()
        for key, value in self.roleNames().items():
            list.append(value)

        return QVariant(list)

db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("mutual_funds.db")
db.open()

accountsModel = QtTabModel(db=db)
accountsModel.setTable("portfolio")
accountsModel.setEditStrategy(QSqlTableModel.OnFieldChange)
accountsModel.select()

# Create an instance of the application
app = QGuiApplication(sys.argv)
# Create QML engine
engine = QQmlApplicationEngine()

engine.rootContext().setContextProperty("accountsModel", accountsModel)

# Load the qml file into the engine
engine.load("app.qml")

engine.quit.connect(app.quit)
sys.exit(app.exec_())
