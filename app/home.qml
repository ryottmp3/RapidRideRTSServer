// TransitHome.qml
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

Rectangle {
    anchors.fill: parent
    border.width: 2
    border.color: "#f5721b"
    color: "#121212"

    signal viewPdfClicked()

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
            font.pointSize: 32
            font.bold: true
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("View Route")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: controller.loadPage("routes.qml")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Purchase Tickets"
            font.pointSize: 20
            font.bold: true
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Purchase Tickets")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: console.log("Purchase Tickets... ")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Open Wallet"
            font.pointSize: 20
            font.bold: true
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Open Wallet")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: console.log("Open Wallet... ")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "View Alerts"
            font.pointSize: 20
            font.bold: true
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("View Alerts")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: console.log("View Alerts... ")
        }

        Button {
            Layout.fillWidth: true
            Layout.fillHeight: true
            text: "Settings"
            font.pointSize: 20
            font.bold: true
            background: Rectangle {
                color: "#1f1f1f"
                border.width: 2
                border.color: "#f5721b"
            }
            contentItem: Text {
                text: qsTr("Settings")
                color: "#ffffff"
                font.pointSize: 20
                anchors.centerIn: parent
            }
            onClicked: console.log("Settings... ")
        }
    }
}

