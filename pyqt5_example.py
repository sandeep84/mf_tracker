import sys

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSlot, QObject, QByteArray, QVariant, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine
from PyQt5.QtWidgets import QWidget, QLabel, QTextEdit, QApplication

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

# Create the application instance.
app = QApplication(sys.argv)

# Register the Python type.  Its URI is 'People', it's v1.0 and the type
# will be called 'Person' in QML.
# qmlRegisterType(Person, 'People', 1, 0, 'Person')

# Create a QML engine.
engine = QQmlEngine()
engine.rootContext().setContextProperty("accountsModel", accountsModel)

# Create a component factory and load the QML script.
component = QQmlComponent(engine)
component.loadUrl(QUrl('app.qml'))

for error in component.errors():
    print(error.toString())

# Create an instance of the component.
person = component.create()

sys.exit(app.exec())