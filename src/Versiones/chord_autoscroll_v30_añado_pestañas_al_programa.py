import sys
import os
import math
import re
import json
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox, QInputDialog, QFontDialog, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent
from PyQt6.QtGui import QTextCursor

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Desactivar el manejo de drops por defecto

class TextScrollerApp(QMainWindow):
# Dentro de la clase `TextScrollerApp`
    def show_about_dialog(self):
        about_text = (
            "<h2><b>Chord autoscroll</b></h2>"
            "<p>Este programa sirve para la transposición de acordes, podrás cargar tus canciones que contengan "
            "letras y acordes para transportarlas fácilmente y desplazarte automáticamente por el texto, "
            "para tus ensayos.</p>"
            "<p>Copyright 2024  Washington Indacochea Delgado.<br>"
            "wachin.id@gmail.com<br>"
            "Licencia GPL 3</p>"
            "<p>Para más información revisa:</p>"
            '<a href="https://github.com/wachin/py_chord_autoscroll">https://github.com/wachin/py_chord_autoscroll</a>'
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Acerca de Chord Autoscroll")
        dialog.setTextFormat(Qt.TextFormat.RichText)  # Permitir formato HTML
        dialog.setText(about_text)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        dialog.exec()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lector y Editor de Letras con Acordes")
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
            current_widget = self.get_current_text_widget()
            if current_widget:
                current_widget.setFont(font)


            # Guardar la fuente seleccionada en la configuración
            self.config['font_family'] = font.family()
            self.config['font_size'] = font.pointSize()
            self.save_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Contenedor de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)

        # Crear la primera pestaña
        self.add_new_tab()

        # Controles para desplazamiento y transposición
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

        # Restaurar la posición del deslizador desde la configuración
        last_position = self.config.get('last_slider_position', 15)
        self.speed_slider.setValue(last_position)

        # Recalcular la velocidad al iniciar el programa
        self.update_speed()

        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)

        self.transpose_button = QPushButton("Transponer")
        self.transpose_button.clicked.connect(self.show_transpose_menu)
        control_layout.addWidget(self.transpose_button)

        self.create_menu_bar()

        self.setAcceptDrops(True)

    def add_new_tab(self, file_name=None, content=""):
        # Crear un nuevo área de texto
        text_widget = CustomTextEdit()
        text_widget.setUndoRedoEnabled(True)

        # Aplicar la fuente predeterminada desde la configuración
        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        text_widget.setFont(QFont(default_font, default_font_size))

        # Cargar contenido si se proporciona
        if content:
            text_widget.setPlainText(content)

        # Agregar el área de texto como nueva pestaña
        tab_name = file_name if file_name else "Nuevo archivo"
        self.tab_widget.addTab(text_widget, tab_name)

        # Establecer como la pestaña activa
        self.tab_widget.setCurrentWidget(text_widget)

    def close_tab(self, index):
        # Cerrar la pestaña en el índice dado
        self.tab_widget.removeTab(index)

    def get_current_text_widget(self):
        # Obtener el área de texto de la pestaña activa
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, CustomTextEdit):
            return widget
        return None

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")

        new_action = QAction("Nuevo archivo", self)
        new_action.triggered.connect(self.add_new_tab)
        new_action.setShortcut("Ctrl+N")  # Atajo: Ctrl+N
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")  # Atajo: Ctrl+O
        file_menu.addAction(open_action)

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")  # Atajo: Ctrl+S
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar como", self)
        save_as_action.triggered.connect(self.save_file)
        save_as_action.setShortcut("Ctrl+Shift+S")  # Atajo: Ctrl+Shift+S
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")  # Atajo: Ctrl+Q
        file_menu.addAction(exit_action)

        # Menú Editar
        edit_menu = menu_bar.addMenu("Editar")

        undo_action = QAction("Deshacer", self)
        undo_action.triggered.connect(lambda: self.get_current_text_widget().undo())
        undo_action.setShortcut("Ctrl+Z")  # Atajo: Ctrl+Z
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.triggered.connect(lambda: self.get_current_text_widget().redo())
        redo_action.setShortcut("Ctrl+Shift+Z")  # Atajo: Ctrl+Shift+Z
        edit_menu.addAction(redo_action)

        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(lambda: self.get_current_text_widget().selectAll())
        select_all_action.setShortcut("Ctrl+A")  # Atajo: Ctrl+A
        edit_menu.addAction(select_all_action)

        # Menú Opciones
        options_menu = menu_bar.addMenu("Opciones")

        # ... Opción de cambiar la fuente
        change_font_action = QAction("Cambiar fuente", self)
        change_font_action.triggered.connect(self.select_font)
        change_font_action.setShortcut("Ctrl+F")
        options_menu.addAction(change_font_action)

        # ... Opción de cambiar la velocidad máxima
        change_speed_action = QAction("Cambiar velocidad máxima", self)
        change_speed_action.triggered.connect(self.change_max_speed)
        change_speed_action.setShortcut("Ctrl+Shift+V")
        options_menu.addAction(change_speed_action)

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")

        about_action = QAction("Acerca de...", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setShortcut("Ctrl+H")
        help_menu.addAction(about_action)

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
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    # Si la pestaña actual está vacía, cargar el contenido aquí
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                else:
                    # Si la pestaña actual no está vacía, abrir en una nueva pestaña
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "El archivo no es válido o no existe.")

    def new_file(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.clear()
        self.current_file = None
        self.setWindowTitle("Lector y Editor de Texto - Nuevo archivo")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()

                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    # Si la pestaña actual está vacía, cargar el contenido aquí
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                else:
                    # Si la pestaña actual no está vacía, abrir en una nueva pestaña
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                current_widget = self.get_current_text_widget()
                if current_widget:
                    current_widget.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def save_file(self):
        text_widget = self.get_current_text_widget()
        if text_widget:
            content = text_widget.toPlainText()
            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos de texto (*.txt)")
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as file:
                        file.write(content)
                    index = self.tab_widget.indexOf(text_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    QMessageBox.information(self, "Guardado", "Archivo guardado exitosamente.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", "", "Archivos de texto (*.txt)")
        if file_path:
            current_widget = self.get_current_text_widget()
            if current_widget:
                content = current_widget.toPlainText()
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
            current_widget = self.get_current_text_widget()
            if current_widget:
                scrollbar = current_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() + 1)
            QTimer.singleShot(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        min_speed = 1
        factor = math.log(self.max_speed / min_speed) / 29
        return max(1, int(min_speed * math.exp(factor * (30 - value))))

    def update_speed(self):
        self.scroll_speed = self.calculate_speed(self.speed_slider.value())
        # Guardar la posición del deslizador en la configuración
        self.config['last_slider_position'] = self.speed_slider.value()
        self.save_config()

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
        # Guardar la posición actual del scroll
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_scroll_position = current_widget.verticalScrollBar().value()

        # Obtener el contenido actual y transponerlo
        current_widget = self.get_current_text_widget()
        if current_widget:
            content = current_widget.toPlainText()
        transposed_content = self.transpose_text(content, semitones)

        # Usar QTextCursor para reemplazar el texto sin perder el historial de deshacer
        current_widget = self.get_current_text_widget()
        if current_widget:
            cursor = current_widget.textCursor()
        cursor.beginEditBlock()  # Agrupa los cambios para que sean una sola acción de deshacer
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(transposed_content)
        cursor.endEditBlock()

        # Restaurar la posición del scroll
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.verticalScrollBar().setValue(current_scroll_position)

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
                    spaces_after -= 1  # Quitar espacio al añadir # o b, solo si hay espacio disponible

            return new_chord, ' ' * spaces_after

        def is_chord_line(line):
            words = line.split()
            matches = [bool(re.fullmatch(chord_pattern, word)) for word in words]
            # Considera la línea como acorde si más del 50% de las palabras coinciden con el patrón de acordes
            return sum(matches) > len(words) / 2

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
                next_pos = chord_positions[i + 1].start() if i + 1 < len(chord_positions) else len(line)
                spaces_after = next_pos - match.end()

                # Transponer el acorde
                new_chord, new_spaces = transpose_chord(match.group(), spaces_after)
                new_line.append(new_chord + new_spaces)

                last_end = next_pos

            # Añadir el resto de la línea después del último acorde
            new_line.append(line[last_end:])
            return ''.join(new_line)

        lines = text.split('\n')
        transposed_lines = [process_line(line) if is_chord_line(line) else line for line in lines]
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
            json.dump(self.config, f, indent=4)  # Guardar con formato legible

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())
