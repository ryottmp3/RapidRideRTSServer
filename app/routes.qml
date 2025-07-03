// TransitHome.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Rectangle {
    anchors.fill: parent
    color: "#121212"

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        ToolBar {
            Layout.fillWidth: true
            contentHeight: 150
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }

            Image {
                width: 400; height: 150
                source: "assets/rapidride.png"
                fillMode: Image.PreserveAspectFit
                anchors.centerIn: parent

                MouseArea {
                    anchors.fill: parent
                    onClicked: controller.loadPage("home.qml")
                }
            }
        }

        // 5 equally spaced buttons
        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "View Routes"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Borglum Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("borglum")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Purchase Tickets"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Coolidge Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("coolidge")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Open Wallet"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Jefferson Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("jefferson")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "View Alerts"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Lincoln Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("lincoln")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Settings"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Roosevelt Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("roosevelt")
        }
        
        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Settings"
            font.pointSize: 20
            background: Rectangle {
                color: "#1f1f1f" 
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Washington Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: backend.open_pdf_viewer("washington")
        }
    }
}

