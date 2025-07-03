// main.qml
import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: root
    visible: true
    width: 480
    height: 800
    title: "RTS RapidRide"

    Loader {
        id: pageLoader
        objectName: "pageLoader"
        anchors.fill: parent
        source: "home.qml"
    }
    
    function loadPage(pageUrl) {
        pageLoader.source = pageUrl;
    }

    onClosing: {
        Qt.quit()
    }
}

