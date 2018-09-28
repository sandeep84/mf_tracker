import QtQuick 2.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.11

ApplicationWindow {
    id: window
    objectName: "Window"
    visible: true

    width:myContent.width
    height:myContent.height

    menuBar: MenuBar {
        Menu {
            title: "File"
            MenuItem { text: "Open..." }
            MenuItem { text: "Close" }
        }

        Menu {
            title: "Help"
            MenuItem { text: "About" }
        }
    }

    TabView {
        id: myContent
        width:1800
        height:1000

        Tab {
            title: "Accounts"
            ScrollView {
                TableView {
                    id: accountsTable
                    width:2000
                    height:900
                    model: accountsModel

                    Component.onCompleted: {
                        var roles = model.roleNameArray()
                        for (var i=0; i<roles.length; i++) {
                            var column = addColumn( Qt.createQmlObject(
                                "import QtQuick.Controls 1.1; TableViewColumn {}",
                                this) )
                            column.role = roles[i]
                            column.title = roles[i]
                        }
                    }
                }
            }
        }
        Tab {
            title: "Active Folios"

            FolioDetails {}
            // FolioSummary {}

            // TableView {
            //     TableViewColumn {
            //         role: "folionum"
            //         title: "Folio#"
            //         width: 100
            //     }
            //     TableViewColumn {
            //         role: "trandate"
            //         title: "Date"
            //         width: 100
            //     }
            //     TableViewColumn {
            //         role: "trantype"
            //         title: "Type"
            //         width: 200
            //     }
            //     TableViewColumn {
            //         role: "tranamt"
            //         title: "Amount"
            //         width: 200
            //     }
            //     TableViewColumn {
            //         role: "tranrate"
            //         title: "Rate"
            //         width: 200
            //     }
            //     TableViewColumn {
            //         role: "tranunits"
            //         title: "Units"
            //         width: 200
            //     }
            //     TableViewColumn {
            //         role: "shiftedcode"
            //         title: "Shifted To"
            //         width: 200
            //     }
            //     TableViewColumn {
            //         role: "comments"
            //         title: "Comments"
            //         width: 200
            //     }
            // }
        }
        Tab {
            title: "Reports"
            ToolBar {
                RowLayout {
                    anchors.fill: parent
                    ComboBox {
                        width: 200
                        model: [ "Account Summary", "Capital Gains" ]
                    }        
                }
            }
        }
    }
}
