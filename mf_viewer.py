import sys
from PyQt5.QtWidgets import (QWidget,
    QGridLayout, QFormLayout, QVBoxLayout, QHBoxLayout,
    QTableView, QGroupBox, QLabel, QLineEdit, QCheckBox, QComboBox,
    QMainWindow, QAction, 
    QApplication)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QSortFilterProxyModel, Qt
from PyQt5.QtGui import QIcon, QPalette
from PyQt5 import QtSql, QtGui, QtCore

from accountsModel import *

class folioProperties(QWidget):
    folioUpdated = pyqtSignal([str])

    def __init__(self, parent=None):
        super().__init__(parent)

        self.model = None
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

    def setModel(self, model):
        self.model = model
        self.updateFields()

    def setIndex(self, idx):
        self.index = idx
        self.updateFields()

    def updateFields(self):
        record = self.model.record(self.index)

        self.folionum = record.value("folionum")
        self.folioUpdated.emit(self.folionum)

        self.folioNumberEdit.setText(record.value("folionum"))
        self.companyNameEdit.setText(record.value("amc"))
        self.fundNameEdit.setText(record.value("folioname"))
        self.optionTypeEdit.setText(record.value("option"))
        self.nameEdit.setText(record.value("folioowner"))
        self.schemeCodeEdit.setText(record.value("foliocode"))
        self.fundTypeEdit.setText(record.value("foliotype"))

class folioDetails(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.index = 0

        self.basisEdit = QLineEdit()
        self.navEdit = QLineEdit()
        self.balanceUnitsEdit = QLineEdit()
        self.currentValueEdit = QLineEdit()
        self.realisedProfitsEdit = QLineEdit()
        self.unrealisedProfitsEdit = QLineEdit()
        self.totalProfitsEdit = QLineEdit()
        self.xirrEdit = QLineEdit()

        layout = QGridLayout()
        layout.addWidget(QLabel("Basis"), 0, 0)
        layout.addWidget(self.basisEdit, 0, 1)
        layout.addWidget(QLabel("Current NAV"), 1, 0)
        layout.addWidget(self.navEdit, 1, 1)
        layout.addWidget(QLabel("Balance Units"), 2, 0)
        layout.addWidget(self.balanceUnitsEdit, 2, 1)
        layout.addWidget(QLabel("Current Value"), 3, 0)
        layout.addWidget(self.currentValueEdit, 3, 1)

        layout.addWidget(QLabel("Realised Profits"), 0, 2)
        layout.addWidget(self.realisedProfitsEdit, 0, 3)
        layout.addWidget(QLabel("Unrealised Profits"), 1, 2)
        layout.addWidget(self.unrealisedProfitsEdit, 1, 3)
        layout.addWidget(QLabel("Total Profits"), 2, 2)
        layout.addWidget(self.totalProfitsEdit, 2, 3)
        layout.addWidget(QLabel("XIRR"), 3, 2)
        layout.addWidget(self.xirrEdit, 3, 3)

        groupbox = QGroupBox("Folio Details")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

        palette = QPalette()
        palette.setColor(QPalette.Base, palette.color(QPalette.Window))
        palette.setColor(QPalette.Text, palette.color(QPalette.WindowText))
        for attr, value in self.__dict__.items():
            if attr.endswith("Edit"):
                value.setReadOnly(True)
                value.setPalette(palette)

    def setModel(self, model):
        self.model = model
        self.updateFields()

    def setIndex(self, idx):
        self.index = idx
        self.updateFields()

    def updateFields(self):
        record = self.model.record(self.index)
        self.basisEdit.setText("{0:.2f}".format(record.value("basis")))
        self.navEdit.setText(str(record.value("currentnav")))
        self.balanceUnitsEdit.setText("{0:.3f}".format(record.value("balanceunits")))
        self.currentValueEdit.setText("{0:.3f}".format(record.value("currentvalue")))
        self.realisedProfitsEdit.setText("{0:.2f}".format(record.value("realisedprofits")))
        self.unrealisedProfitsEdit.setText("{0:.2f}".format(record.value("unrealisedprofits")))
        self.totalProfitsEdit.setText("{0:.2f}".format(record.value("totalprofits")))
        self.xirrEdit.setText("{0:.2%}".format(record.value("xirr")))

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
        self.index = 0
        self.model = accountsModel()

        self.folioProps = folioProperties()
        self.folioDetails = folioDetails()
        self.tranTable = transactionTable()

        self.folioProps.setModel(self.model)
        self.folioDetails.setModel(self.model)
        self.folioProps.folioUpdated.connect(self.tranTable.model.updateFolioFilter)

        grid = QGridLayout(self)
        grid.addWidget(self.folioProps, 0, 0)
        grid.addWidget(self.folioDetails, 0, 1)
        grid.addWidget(self.tranTable, 1, 0, 1, 2)

        self.updateFields()

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
        if self.index < self.model.rowCount() - 1:
            self.index = self.index + 1
            self.updateFields()

    @pyqtSlot()
    def decrementIndex(self):
        if self.index > 0:
            self.index = self.index - 1
            self.updateFields()

    def updateFields(self):
        self.folioProps.setIndex(self.index)
        self.folioDetails.setIndex(self.index)

class reportUI(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.index = 0
        self.selectActiveOnly = False

        self.srcModel = accountsModel()
        self.proxyModel = QSortFilterProxyModel()

        self.proxyModel.setSourceModel(self.srcModel)
        
        self.reportChooser = QComboBox()
        self.reportChooser.addItems(["Active Folios", "All Folios"])
        self.reportChooser.currentTextChanged.connect(self.filterChanged)
        self.filterChanged(self.reportChooser.currentText())

        self.reportTableView = QTableView()
        self.reportTableView.setModel(self.proxyModel)
        self.reportTableView.setSortingEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.reportChooser)
        layout.addWidget(self.reportTableView)

        groupbox = QGroupBox("Account Summary")
        groupbox.setLayout(layout)

        boxLayout = QVBoxLayout(self)
        boxLayout.addWidget(groupbox)

    @pyqtSlot(str)
    def filterChanged(self, filter):
        if filter == "Active Folios":
            self.proxyModel.setFilterRegExp("^[1-9].*")
            self.proxyModel.setFilterKeyColumn(9)
        else:
            self.proxyModel.setFilterRegExp(".*")

class mainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.createTransactionWindow()
        self.showMaximized()
        
    def initUI(self):
        self.homeAct = QAction(QIcon.fromTheme("go-home"), 'Home', self)
        self.homeAct.setStatusTip('Home')
        self.homeAct.triggered.connect(self.createTransactionWindow)

        self.reportAct = QAction(QIcon.fromTheme("x-office-document"), 'Report', self)
        self.reportAct.setStatusTip('Generate Report')
        self.reportAct.triggered.connect(self.createReportWindow)

        self.newItemAct = QAction(QIcon.fromTheme("list-add"), 'New', self)
        self.newItemAct.setShortcut('Ctrl+N')
        self.newItemAct.setStatusTip('New account')

        self.removeItemAct = QAction(QIcon.fromTheme("list-remove"), 'New', self)
        self.removeItemAct.setStatusTip('Remove account')

        self.firstItemAct = QAction(QIcon.fromTheme("media-skip-backward"), 'First', self)
        self.firstItemAct.setStatusTip('First account')

        self.previousItemAct = QAction(QIcon.fromTheme("media-seek-backward"), 'Previous', self)
        self.previousItemAct.setShortcut('PgUp')
        self.previousItemAct.setStatusTip('Previous account')

        self.nextItemAct = QAction(QIcon.fromTheme("media-seek-forward"), 'Next', self)
        self.nextItemAct.setShortcut('PgDown')
        self.nextItemAct.setStatusTip('Next account')

        self.lastItemAct = QAction(QIcon.fromTheme("media-skip-forward"), 'Last', self)
        self.lastItemAct.setStatusTip('Last account')

        self.updateNAVAct = QAction(QIcon.fromTheme("emblem-synchronizing"), 'Update NAV', self)
        self.updateNAVAct.setStatusTip('Update NAV')

        #self.statusBar()

        #menubar = self.menuBar()
        #fileMenu = menubar.addMenu('&File')
        #fileMenu.addAction(exitAct)

        self.toolbar = self.addToolBar("Navigation")
        self.toolbar.addAction(self.homeAct)
        self.toolbar.addAction(self.reportAct)
        self.toolbar.addAction(self.updateNAVAct)

        self.toolbar.addSeparator()
        self.toolbar.addAction(self.newItemAct)
        self.toolbar.addAction(self.removeItemAct)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.firstItemAct)
        self.toolbar.addAction(self.previousItemAct)
        self.toolbar.addAction(self.nextItemAct)
        self.toolbar.addAction(self.lastItemAct)

        self.setWindowTitle('Mutual Funds')

    @pyqtSlot()
    def createTransactionWindow(self):
        self.transactionUI = transactionUI()
        self.setCentralWidget(self.transactionUI)

        self.newItemAct.setEnabled(True)
        self.removeItemAct.setEnabled(True)
        self.firstItemAct.setEnabled(True)
        self.previousItemAct.setEnabled(True)
        self.nextItemAct.setEnabled(True)
        self.lastItemAct.setEnabled(True)

        self.firstItemAct.triggered.connect(self.transactionUI.firstIndex)
        self.previousItemAct.triggered.connect(self.transactionUI.decrementIndex)
        self.nextItemAct.triggered.connect(self.transactionUI.incrementIndex)
        self.lastItemAct.triggered.connect(self.transactionUI.lastIndex)
        self.updateNAVAct.triggered.connect(self.transactionUI.model.updateNAV)

    @pyqtSlot()
    def createReportWindow(self):
        self.reportUI = reportUI()
        self.setCentralWidget(self.reportUI)

        self.newItemAct.setEnabled(False)
        self.removeItemAct.setEnabled(False)
        self.firstItemAct.setEnabled(False)
        self.previousItemAct.setEnabled(False)
        self.nextItemAct.setEnabled(False)
        self.lastItemAct.setEnabled(False)

        self.updateNAVAct.triggered.connect(self.reportUI.srcModel.updateNAV)
        
if __name__ == '__main__':
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('mutual_funds.db')

    app = QApplication(sys.argv)
    ex = mainWindow()
    ex.show()
    sys.exit(app.exec_())