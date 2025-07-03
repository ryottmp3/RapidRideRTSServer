# Main
# Copyright 2025
# MIT License

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal
from ticketing import TicketGenerator, TicketValidator


class PdfViewer(QMainWindow):
    def __init__(self, pdf_path):
        super().__init__()
        self.setWindowTitle("PDF Viewer")

        self.pdf_document = QPdfDocument(self)
        self.pdf_document.load(pdf_path)

        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_document)

        self.setCentralWidget(self.pdf_view)
        self.resize(800, 600)


class Controller(QObject):
    def __init__(self, loader):
        super().__init__()
        self.loader = loader

    @Slot(str)
    def loadPage(self, page):
        self.loader.setProperty("source", page)


class AppBackend(QObject):
    def __init__(self):
        super().__init__()
        self._windows = []

    @Slot(str)
    def open_pdf_viewer(self, fname: str):
        viewer = PdfViewer(f"assets/routes/{fname}-map2025.pdf")
        viewer.show()
        self._windows.append(viewer)  # Prevent garbage collection

    @Slot(str)
    def purchase_ticket(self, ticket_type: str):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    engine = QQmlApplicationEngine()
    engine.load("main.qml")

    if not engine.rootObjects():
        sys.exit(-1)

    root = engine.rootObjects()[0]
    loader = root.findChild(QObject, "pageLoader")

    controller = Controller(loader)
    backend = AppBackend()

    engine.rootContext().setContextProperty("controller", controller)
    engine.rootContext().setContextProperty("backend", backend)

    sys.exit(app.exec())
