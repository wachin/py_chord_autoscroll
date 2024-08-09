import sys
import os
import math
import re
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent

class TextScrollerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lector y Editor de Texto")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.scroll_speed = self.calculate_speed(15)  # Default speed

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.text_widget = QTextEdit()
        layout.addWidget(self.text_widget)

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_scrolling)
        control_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_scrolling)
        control_layout.addWidget(self.pause_button)

        control_layout.addWidget(QLabel("Velocidad:"))

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 30)
        self.speed_slider.setValue(15)
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)

        self.transpose_button = QPushButton("Transponer")
        self.transpose_button.clicked.connect(self.show_transpose_menu)
        control_layout.addWidget(self.transpose_button)

        self.create_menu_bar()

        self.setAcceptDrops(True)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("Archivo")
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            self.text_widget.setPlainText(content)
        self.current_file = file_path
        self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")

    def save_file(self):
        if self.current_file:
            content = self.text_widget.toPlainText()
            with open(self.current_file, 'w') as file:
                file.write(content)
            QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente.")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            content = self.text_widget.toPlainText()
            with open(file_path, 'w') as file:
                file.write(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
            QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().urls()[0].toLocalFile().endswith('.txt'):
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_path = event.mimeData().urls()[0].toLocalFile()
        self.load_file(file_path)

    def start_scrolling(self):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_text()

    def pause_scrolling(self):
        self.is_scrolling = False

    def scroll_text(self):
        if self.is_scrolling:
            scrollbar = self.text_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() + 1)
            QTimer.singleShot(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        min_speed = 320
        max_speed = 6400
        factor = math.log(max_speed / min_speed) / 29
        return int(min_speed * math.exp(factor * (30 - value)))

    def update_speed(self):
        self.scroll_speed = self.calculate_speed(self.speed_slider.value())

    def show_transpose_menu(self):
        transpose_menu = QMenu(self)
        for i in range(-7, 8):
            action = QAction(f"{i:+d}" if i != 0 else "0 (Original)", self)
            action.triggered.connect(lambda checked, x=i: self.transpose_chords(x))
            transpose_menu.addAction(action)
        transpose_menu.exec(self.transpose_button.mapToGlobal(self.transpose_button.rect().bottomLeft()))

    def transpose_chords(self, semitones):
        content = self.text_widget.toPlainText()
        transposed_content = self.transpose_text(content, semitones)
        self.text_widget.setPlainText(transposed_content)

    def transpose_text(self, text, semitones):
        chord_pattern = r'\b[A-G](#|b)?(m|dim|dim7|aug|maj|min|sus|bm|add)?[0-9]?(?:\s|$)'

        def transpose_chord(match):
            chord = match.group(0)
            root = chord[0]
            sharp_flat = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + sharp_flat):]

            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            index = notes.index(root + sharp_flat) if root + sharp_flat in notes else notes.index(root)
            new_index = (index + semitones) % 12
            new_root = notes[new_index]

            return new_root + suffix

        return re.sub(chord_pattern, transpose_chord, text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())
