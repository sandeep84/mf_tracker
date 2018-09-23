import QtQuick.Controls 1.4
import QtQuick.Layouts 1.11

GridLayout {
    id: folioDetails
    columns: 2
    
    Label { text: "Folio Number" }
    TextField { placeholderText: "Folio Number" }

    Label { text: "Company Name" }
    TextField { placeholderText: "Company Name" }

    Label { text: "Fund Name" }
    TextField { placeholderText: "Fund Name" }

    Label { text: "Option Type" }
    TextField { placeholderText: "Option Type" }

    Label { text: "Name" }
    TextField { placeholderText: "Name" }

    Label { text: "Scheme Code" }
    TextField { placeholderText: "Scheme Code" }

    Label { text: "Fund Type" }
    TextField { placeholderText: "Fund Type" }
}