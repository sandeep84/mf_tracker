import sys
from PyQt5.QtWidgets import (QWidget,
    QGridLayout, QFormLayout, QVBoxLayout, QHBoxLayout,
    QTableView, QGroupBox, QLabel, QLineEdit, QMainWindow, QAction,
    QApplication)
from PyQt5.QtGui import QIcon
from PyQt5 import QtSql, QtGui, QtCore

class folioProperties(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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

class transactionModel(QtSql.QSqlTableModel):
    def __init__(self):
        super().__init__()
        
        self.setTable('transactions') 
        self.setEditStrategy(QtSql.QSqlTableModel.OnFieldChange)
        self.select()
        self.removeColumn(0)

class transactionTable(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        model = transactionModel()
        transactionsTableView = QTableView()
        transactionsTableView.setModel(model)
        
        layout = QVBoxLayout()
        layout.addWidget(transactionsTableView)

        groupbox = QGroupBox("Transactions")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

class transactionUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        grid = QGridLayout(self)
        grid.addWidget(folioProperties(), 0, 0)
        grid.addWidget(folioDetails(), 0, 1)
        grid.addWidget(transactionTable(), 1, 0, 1, 2)


class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setCentralWidget(transactionUI())

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

        previousItemAct = QAction(QIcon.fromTheme("media-seek-backward"), 'Previous', self)
        previousItemAct.setShortcut('Ctrl+Left')
        previousItemAct.setStatusTip('Previous account')

        nextItemAct = QAction(QIcon.fromTheme("media-seek-forward"), 'Next', self)
        nextItemAct.setShortcut('Ctrl+Right')
        nextItemAct.setStatusTip('Next account')

        lastItemAct = QAction(QIcon.fromTheme("media-skip-forward"), 'Last', self)
        lastItemAct.setStatusTip('Last account')

        reportAct = QAction(QIcon.fromTheme("x-office-document"), 'Last', self)
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