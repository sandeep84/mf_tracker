import sys
from PyQt5.QtWidgets import (QWidget,
    QGridLayout, QFormLayout, QVBoxLayout, QHBoxLayout,
    QTableView, QGroupBox, QLabel, QLineEdit, QMainWindow, QAction,
    QApplication)
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5 import QtSql, QtGui, QtCore

class folioProperties(QWidget):
    folioUpdated = pyqtSignal([str])

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = accountsModel()
        self.index = 0
        self.folionum = None

        self.folioNumberEdit = QLineEdit()
        self.companyNameEdit = QLineEdit()
        self.fundNameEdit = QLineEdit()
        self.optionTypeEdit = QLineEdit()
        self.nameEdit = QLineEdit()
        self.schemeCodeEdit = QLineEdit()
        self.fundTypeEdit = QLineEdit()

        layout = QFormLayout()
        layout.addRow("Folio Number",   self.folioNumberEdit)
        layout.addRow("Company Name",   self.companyNameEdit)
        layout.addRow("Fund Name",      self.fundNameEdit)
        layout.addRow("Option Type",    self.optionTypeEdit)
        layout.addRow("Name",           self.nameEdit)
        layout.addRow("Scheme Code",    self.schemeCodeEdit)
        layout.addRow("Fund Type",      self.fundTypeEdit)

        groupbox = QGroupBox("Folio Properties")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

        self.updateFields()

    def updateFields(self):
        self.folionum = self.model.record(self.index).value("folionum")
        self.folioUpdated.emit(self.folionum)

        self.folioNumberEdit.setText(self.model.record(self.index).value("folionum"))
        self.companyNameEdit.setText(self.model.record(self.index).value("amc"))
        self.fundNameEdit.setText(self.model.record(self.index).value("folioname"))
        self.optionTypeEdit.setText(self.model.record(self.index).value("option"))
        self.nameEdit.setText(self.model.record(self.index).value("folioowner"))
        self.schemeCodeEdit.setText(self.model.record(self.index).value("foliocode"))
        self.fundTypeEdit.setText(self.model.record(self.index).value("foliotype"))

    @pyqtSlot()
    def firstIndex(self):
        self.index = 0
        self.updateFields()

    @pyqtSlot()
    def lastIndex(self):
        self.index = self.model.rowCount() - 1
        self.updateFields()

    @pyqtSlot()
    def incrementIndex(self):
        self.index = self.index + 1
        self.updateFields()

    @pyqtSlot()
    def decrementIndex(self):
        self.index = self.index - 1
        self.updateFields()

class folioDetails(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        basisEdit = QLineEdit()
        navEdit = QLineEdit()
        balanceUnitsEdit = QLineEdit()
        currentValueEdit = QLineEdit()
        realisedProfitsEdit = QLineEdit()
        unrealisedProfitsEdit = QLineEdit()
        totalProfitsEdit = QLineEdit()
        xirrEdit = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(QLabel("Basis"), 0, 0)
        layout.addWidget(basisEdit, 0, 1)
        layout.addWidget(QLabel("Current NAV"), 1, 0)
        layout.addWidget(navEdit, 1, 1)
        layout.addWidget(QLabel("Balance Units"), 2, 0)
        layout.addWidget(balanceUnitsEdit, 2, 1)
        layout.addWidget(QLabel("Current Value"), 3, 0)
        layout.addWidget(currentValueEdit, 3, 1)

        layout.addWidget(QLabel("Realised Profits"), 0, 2)
        layout.addWidget(realisedProfitsEdit, 0, 3)
        layout.addWidget(QLabel("Unrealised Profits"), 1, 2)
        layout.addWidget(unrealisedProfitsEdit, 1, 3)
        layout.addWidget(QLabel("Total Profits"), 2, 2)
        layout.addWidget(totalProfitsEdit, 2, 3)
        layout.addWidget(QLabel("XIRR"), 3, 2)
        layout.addWidget(xirrEdit, 3, 3)

        groupbox = QGroupBox("Folio Details")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

class accountsModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()
        
        self.setTable('portfolio') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()

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

class transactionTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = transactionModel()
        transactionsTableView = QTableView()
        transactionsTableView.setModel(self.model)
        
        layout = QVBoxLayout()
        layout.addWidget(transactionsTableView)

        groupbox = QGroupBox("Transactions")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

class transactionUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.folioProps = folioProperties()
        self.folioDetails = folioDetails()
        self.tranTable = transactionTable()

        self.folioProps.folioUpdated.connect(self.tranTable.model.updateFolioFilter)

        grid = QGridLayout(self)
        grid.addWidget(self.folioProps, 0, 0)
        grid.addWidget(self.folioDetails, 0, 1)
        grid.addWidget(self.tranTable, 1, 0, 1, 2)


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.transactionUI = transactionUI()
        self.setCentralWidget(self.transactionUI)

        exitAct = QAction(QIcon.fromTheme("application-exit"), 'Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(self.close)

        newItemAct = QAction(QIcon.fromTheme("list-add"), 'New', self)
        newItemAct.setShortcut('Ctrl+N')
        newItemAct.setStatusTip('New account')
        #newItemAct.triggered.connect(self.close)
        
        removeItemAct = QAction(QIcon.fromTheme("list-remove"), 'New', self)
        removeItemAct.setStatusTip('Remove account')
#        removeItemAct.triggered.connect(self.close)

        firstItemAct = QAction(QIcon.fromTheme("media-skip-backward"), 'First', self)
        firstItemAct.setStatusTip('First account')
        firstItemAct.triggered.connect(self.transactionUI.folioProps.firstIndex)

        previousItemAct = QAction(QIcon.fromTheme("media-seek-backward"), 'Previous', self)
        previousItemAct.setShortcut('Ctrl+Left')
        previousItemAct.setStatusTip('Previous account')
        previousItemAct.triggered.connect(self.transactionUI.folioProps.decrementIndex)

        nextItemAct = QAction(QIcon.fromTheme("media-seek-forward"), 'Next', self)
        nextItemAct.setShortcut('Ctrl+Right')
        nextItemAct.setStatusTip('Next account')
        nextItemAct.triggered.connect(self.transactionUI.folioProps.incrementIndex)

        lastItemAct = QAction(QIcon.fromTheme("media-skip-forward"), 'Last', self)
        lastItemAct.setStatusTip('Last account')
        lastItemAct.triggered.connect(self.transactionUI.folioProps.lastIndex)

        reportAct = QAction(QIcon.fromTheme("x-office-document"), 'Report', self)
        reportAct.setStatusTip('Generate Report')

        #self.statusBar()

        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAct)

        toolbar = self.addToolBar('Exit')
        toolbar.addAction(newItemAct)
        toolbar.addAction(removeItemAct)
        toolbar.addSeparator()
        toolbar.addAction(firstItemAct)
        toolbar.addAction(previousItemAct)
        toolbar.addAction(nextItemAct)
        toolbar.addAction(lastItemAct)
        toolbar.addSeparator()
        toolbar.addAction(reportAct)

        self.setWindowTitle('Mutual Funds')

if __name__ == '__main__':
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('mutual_funds.db')

    app = QApplication(sys.argv)
    ex = mainWindow()
    ex.show()
    sys.exit(app.exec_())