import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QMessageBox
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class TextScrollerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("Lector y Editor de Texto")
        self.setGeometry(100, 100, 800, 600)

        # Crear widget de texto
        self.text_widget = QTextEdit(self)
        self.setCentralWidget(self.text_widget)

        # Permitir arrastrar y soltar
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        # Verificar si el contenido arrastrado es una URL (archivo)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.txt'):
                self.load_file(file_path)
            else:
                event.ignore()
        else:
            event.ignore()

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_widget.setPlainText(content)
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())
