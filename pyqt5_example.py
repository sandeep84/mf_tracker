import sys

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import pyqtProperty, QCoreApplication, QObject, QUrl
from PyQt5.QtQml import qmlRegisterType, QQmlComponent, QQmlEngine
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt


db = QSqlDatabase.addDatabase("QSQLITE")
db.setDatabaseName("mutual_funds.db")
db.open()

accountsModel =  QtSql.QSqlRelationalTableModel(db=db)
accountsModel.setTable("portfolio")
accountsModel.setEditStrategy(QSqlTableModel.OnManualSubmit)
print(accountsModel.setHeaderData(0, Qt.Horizontal, "Folio"))
print(accountsModel.setHeaderData(1, Qt.Horizontal, "Name"))
print(accountsModel.setHeaderData(2, Qt.Horizontal, "Hello"))
accountsModel.select()

# Create the application instance.
app = QGuiApplication(sys.argv)

# Register the Python type.  Its URI is 'People', it's v1.0 and the type
# will be called 'Person' in QML.
# qmlRegisterType(Person, 'People', 1, 0, 'Person')

# Create a QML engine.
engine = QQmlEngine()
engine.rootContext().setContextProperty("accountsModel", accountsModel)

# Create a component factory and load the QML script.
component = QQmlComponent(engine)
component.loadUrl(QUrl('app.qml'))

# Create an instance of the component.
person = component.create()

sys.exit(app.exec())