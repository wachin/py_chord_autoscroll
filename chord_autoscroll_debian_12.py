import sys
import os
import math
import re
import json
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox, QInputDialog, QFontDialog)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QAction, QDragEnterEvent, QDropEvent

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Desactivar el manejo de drops por defecto

class TextScrollerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lector y Editor de Texto")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 400  # Velocidad máxima predeterminada
        self.scroll_speed = self.calculate_speed(15)  # Velocidad predeterminada

        self.config_file = 'config12.json'

        # Inicializar configuración antes de usarla
        self.config = {}
        self.load_config()

        self.init_ui()

    def select_font(self):
        # Abrir diálogo de selección de fuente
        font, ok = QFontDialog.getFont(QFont(self.config.get('font_family', 'Noto Mono'),
                                            self.config.get('font_size', 10)),
                                    self, "Selecciona una fuente")

        # Si el usuario selecciona una fuente y presiona OK
        if ok:
            # Aplicar la fuente seleccionada al área de texto
            self.text_widget.setFont(font)

            # Guardar la fuente seleccionada en la configuración
            self.config['font_family'] = font.family()
            self.config['font_size'] = font.pointSize()
            self.save_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.text_widget = CustomTextEdit()

        # Aplicar la fuente predeterminada desde la configuración
        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        self.text_widget.setFont(QFont(default_font, default_font_size))

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

        new_action = QAction("Nuevo archivo", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar como", self)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("Editar")
        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(self.text_widget.selectAll)
        edit_menu.addAction(select_all_action)

        options_menu = menu_bar.addMenu("Opciones")

        # Añadir la opción de cambiar la fuente
        change_font_action = QAction("Cambiar fuente", self)
        change_font_action.triggered.connect(self.select_font)
        options_menu.addAction(change_font_action)

        change_speed_action = QAction("Cambiar velocidad máxima", self)
        change_speed_action.triggered.connect(self.change_max_speed)
        options_menu.addAction(change_speed_action)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.open_dropped_file(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def open_dropped_file(self, file_path):
        if os.path.exists(file_path) and file_path.lower().endswith('.txt'):
            self.load_file(file_path)
        else:
            QMessageBox.warning(self, "Error", "El archivo no es válido o no existe.")

    def new_file(self):
        self.text_widget.clear()
        self.current_file = None
        self.setWindowTitle("Lector y Editor de Texto - Nuevo archivo")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_widget.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def save_file(self):
        if self.current_file:
            content = self.text_widget.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente.")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            content = self.text_widget.toPlainText()
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
            QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente.")

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
        min_speed = 1
        factor = math.log(self.max_speed / min_speed) / 29
        return max(1, int(min_speed * math.exp(factor * (30 - value))))

    def update_speed(self):
        self.scroll_speed = self.calculate_speed(self.speed_slider.value())

    def change_max_speed(self):
        new_max_speed, ok = QInputDialog.getInt(
            self, "Cambiar velocidad máxima",
            "Ingrese la nueva velocidad máxima (1-1000):",
            value=self.max_speed, min=1, max=1000
        )
        if ok:
            self.max_speed = new_max_speed
            self.update_speed()
            self.save_config()
            QMessageBox.information(self, "Velocidad actualizada",
                                    f"La velocidad máxima se ha actualizado a {self.max_speed}.\n"
                                    f"Use el control deslizante para ajustar la velocidad entre 1 y {self.max_speed}.")

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
        chord_pattern = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)'

        chord_base = [
            ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'],
            ['F#', 'Gb'], ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
        ]

        def transpose_chord(chord, spaces_after):
            root = chord[0]
            accidental = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + accidental):]

            current_index = next(i for i, group in enumerate(chord_base) if root + accidental in group)
            new_index = (current_index + semitones) % len(chord_base)
            new_root = chord_base[new_index][0]

            if len(chord_base[new_index]) > 1:
                new_root = chord_base[new_index][0] if semitones > 0 else chord_base[new_index][1]

            new_chord = new_root + suffix

            # Ajustar espacios
            if accidental and not ('#' in new_chord or 'b' in new_chord):
                spaces_after += 1  # Añadir espacio al quitar # o b
            elif not accidental and ('#' in new_chord or 'b' in new_chord):
                if spaces_after > 0:
                    spaces_after -= 0  # Quitar espacio al añadir # o b, solo si hay espacio disponible

            return new_chord, ' ' * spaces_after

        def process_line(line):
            chord_positions = list(re.finditer(chord_pattern, line))
            if not chord_positions:
                return line

            new_line = []
            last_end = 0

            for i, match in enumerate(chord_positions):
                # Añadir el texto entre acordes
                new_line.append(line[last_end:match.start()])

                # Calcular espacios después del acorde
                next_pos = chord_positions[i+1].start() if i+1 < len(chord_positions) else len(line)
                spaces_after = next_pos - match.end()

                # Transponer el acorde
                new_chord, new_spaces = transpose_chord(match.group(), spaces_after)
                new_line.append(new_chord + new_spaces)

                last_end = next_pos

            # Añadir el resto de la línea después del último acorde
            new_line.append(line[last_end:])

            return ''.join(new_line)

        lines = text.split('\n')
        transposed_lines = [process_line(line) for line in lines]
        return '\n'.join(transposed_lines)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'max_speed': 100,
                'font_family': 'Noto Mono',  # Fuente predeterminada
                'font_size': 10  # Tamaño de fuente predeterminado
            }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())
