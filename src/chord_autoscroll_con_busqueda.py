
import sys
import os
import math
import re
import json
import chardet
import enchant
from PyQt6.QtGui import (QFont, QAction, QActionGroup, QDragEnterEvent, QDropEvent, QTextCursor,
                         QShortcut, QKeySequence, QTextCharFormat, QColor, QSyntaxHighlighter,
                         QTextDocument, QContextMenuEvent)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox, QInputDialog, QFontDialog, QTabWidget,
                             QDialog, QLineEdit, QCheckBox, QGridLayout, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QUrl, QTranslator, QLocale, QLibraryInfo, QRegularExpression


class SpellChecker(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell_dict = None
        self.current_language = 'es'
        self.load_dictionary()
        
        # Formato para palabras mal escritas
        self.misspelled_format = QTextCharFormat()
        self.misspelled_format.setUnderlineColor(QColor(255, 0, 0))
        self.misspelled_format.setUnderlineStyle(QTextCharFormat.UnderlineStyle.WaveUnderline)
        
    def load_dictionary(self):
        try:
            self.spell_dict = enchant.Dict(self.current_language)
        except enchant.errors.DictNotFoundError:
            try:
                self.spell_dict = enchant.Dict("en_US")
                self.current_language = 'en_US'
            except:
                self.spell_dict = None
                
    def change_language(self, language):
        try:
            self.spell_dict = enchant.Dict(language)
            self.current_language = language
            self.rehighlight()
        except enchant.errors.DictNotFoundError:
            QMessageBox.warning(None, "Error", f"Diccionario {language} no encontrado")
            
    def highlightBlock(self, text):
        if not self.spell_dict:
            return
            
        # Patrón para palabras (solo letras)
        word_pattern = QRegularExpression(r'\b[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ]+\b')
        iterator = word_pattern.globalMatch(text)
        
        while iterator.hasNext():
            match = iterator.next()
            word = match.captured(0)
            
            # Verificar si la palabra está mal escrita
            if not self.spell_dict.check(word):
                self.setFormat(match.capturedStart(), match.capturedLength(), self.misspelled_format)


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.setWindowTitle("Buscar y Reemplazar")
        self.setModal(True)
        self.resize(400, 200)
        
        layout = QGridLayout()
        
        # Campo de búsqueda
        layout.addWidget(QLabel("Buscar:"), 0, 0)
        self.find_input = QLineEdit()
        layout.addWidget(self.find_input, 0, 1)
        
        # Campo de reemplazo
        layout.addWidget(QLabel("Reemplazar:"), 1, 0)
        self.replace_input = QLineEdit()
        layout.addWidget(self.replace_input, 1, 1)
        
        # Opciones
        self.case_sensitive = QCheckBox("Coincidencia exacta")
        layout.addWidget(self.case_sensitive, 2, 0)
        
        self.whole_word = QCheckBox("Palabra completa")
        layout.addWidget(self.whole_word, 2, 1)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.find_button = QPushButton("Buscar")
        self.find_button.clicked.connect(self.find_text)
        buttons_layout.addWidget(self.find_button)
        
        self.find_prev_button = QPushButton("Buscar anterior")
        self.find_prev_button.clicked.connect(self.find_previous)
        buttons_layout.addWidget(self.find_prev_button)
        
        self.replace_button = QPushButton("Reemplazar")
        self.replace_button.clicked.connect(self.replace_text)
        buttons_layout.addWidget(self.replace_button)
        
        self.replace_all_button = QPushButton("Reemplazar todo")
        self.replace_all_button.clicked.connect(self.replace_all)
        buttons_layout.addWidget(self.replace_all_button)
        
        self.highlight_button = QPushButton("Resaltar todo")
        self.highlight_button.clicked.connect(self.highlight_all)
        buttons_layout.addWidget(self.highlight_button)
        
        layout.addLayout(buttons_layout, 3, 0, 1, 2)
        
        self.setLayout(layout)
        
        # Conectar Enter para buscar
        self.find_input.returnPressed.connect(self.find_text)
        
    def get_text_widget(self):
        return self.parent_widget.get_current_text_widget()
        
    def find_text(self):
        text_widget = self.get_text_widget()
        if not text_widget:
            return
            
        search_text = self.find_input.text()
        if not search_text:
            return
            
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        found = text_widget.find(search_text, flags)
        if not found:
            QMessageBox.information(self, "Búsqueda", "No se encontró el texto")
            
    def find_previous(self):
        text_widget = self.get_text_widget()
        if not text_widget:
            return
            
        search_text = self.find_input.text()
        if not search_text:
            return
            
        flags = QTextDocument.FindFlag.FindBackward
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        found = text_widget.find(search_text, flags)
        if not found:
            QMessageBox.information(self, "Búsqueda", "No se encontró el texto")
            
    def replace_text(self):
        text_widget = self.get_text_widget()
        if not text_widget:
            return
            
        cursor = text_widget.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            
    def replace_all(self):
        text_widget = self.get_text_widget()
        if not text_widget:
            return
            
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            return
            
        content = text_widget.toPlainText()
        flags = 0 if self.case_sensitive.isChecked() else re.IGNORECASE
        
        if self.whole_word.isChecked():
            pattern = r'\b' + re.escape(search_text) + r'\b'
        else:
            pattern = re.escape(search_text)
            
        new_content = re.sub(pattern, replace_text, content, flags=flags)
        count = len(re.findall(pattern, content, flags=flags))
        
        cursor = text_widget.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(new_content)
        cursor.endEditBlock()
        
        QMessageBox.information(self, "Reemplazar", f"Se reemplazaron {count} coincidencias")
        
    def highlight_all(self):
        text_widget = self.get_text_widget()
        if not text_widget:
            return
            
        search_text = self.find_input.text()
        if not search_text:
            return
            
        # Limpiar resaltado anterior
        cursor = text_widget.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.SelectionType.Document)
        format = QTextCharFormat()
        cursor.mergeCharFormat(format)
        cursor.endEditBlock()
        
        # Resaltar todas las coincidencias
        flags = QTextDocument.FindFlag(0)
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindFlag.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindFlag.FindWholeWords
            
        cursor = text_widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor(255, 255, 0))  # Amarillo
        
        while True:
            cursor = text_widget.document().find(search_text, cursor, flags)
            if cursor.isNull():
                break
            cursor.mergeCharFormat(highlight_format)


class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)
        self.spell_checker = SpellChecker(self.document())
        
    def contextMenuEvent(self, event: QContextMenuEvent):
        menu = self.createStandardContextMenu()
        
        # Obtener la palabra bajo el cursor
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if word and self.spell_checker.spell_dict:
            if not self.spell_checker.spell_dict.check(word):
                menu.addSeparator()
                suggestions = self.spell_checker.spell_dict.suggest(word)[:5]
                
                if suggestions:
                    for suggestion in suggestions:
                        action = menu.addAction(f"Sugerir: {suggestion}")
                        action.triggered.connect(lambda checked, s=suggestion, c=cursor: self.replace_word(c, s))
                else:
                    menu.addAction("No hay sugerencias").setEnabled(False)
                    
                menu.addSeparator()
                add_action = menu.addAction("Añadir al diccionario")
                add_action.triggered.connect(lambda: self.add_to_dictionary(word))
                
        menu.exec(event.globalPos())
        
    def replace_word(self, cursor, word):
        cursor.insertText(word)
        
    def add_to_dictionary(self, word):
        try:
            self.spell_checker.spell_dict.add(word)
            self.spell_checker.rehighlight()
            QMessageBox.information(self, "Diccionario", f"'{word}' añadido al diccionario")
        except:
            QMessageBox.warning(self, "Error", "No se pudo añadir la palabra al diccionario")
            
    def set_spell_language(self, language):
        self.spell_checker.change_language(language)


class TextScrollerApp(QMainWindow):
    def show_about_dialog(self):
        about_text = (
            "<h2><b>Chord autoscroll</b></h2>"
            "<p>Este programa sirve para la transposición de acordes, podrás cargar tus canciones que contengan "
            "letras y acordes para transportarlas fácilmente y desplazarte automáticamente por el texto, "
            "para tus ensayos.</p>"
            "<p>Copyright 2025  Washington Indacochea Delgado.<br>"
            "wachin.id@gmail.com<br>"
            "Licencia GPL 3</p>"
            "<p>Para más información revisa:</p>"
            '<a href="https://github.com/wachin/py_chord_autoscroll">https://github.com/wachin/py_chord_autoscroll</a>'
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Acerca de Chord Autoscroll")
        dialog.setTextFormat(Qt.TextFormat.RichText)
        dialog.setText(about_text)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        dialog.exec()

    def __init__(self):
        super().__init__()
        self.translator = QTranslator()

        translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        print(f"Ruta de traducciones: {translations_path}")

        if self.translator.load("qtbase_es", translations_path):
            QApplication.installTranslator(self.translator)
            print("Traducción al español cargada correctamente.")
        else:
            print("No se pudo cargar la traducción al español.")

        self.setWindowTitle("Lector y Editor de Letras con Acordes")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 400
        self.scroll_speed = self.calculate_speed(15)

        self.config_file = 'config12.json'
        self.opened_files = {}
        self.file_encodings = {}
        self.config = {}
        self.load_config()

        self.find_replace_dialog = None
        
        self.init_ui()
        self.update_recent_files_menu()

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
        last_position = self.config.get('last_slider_position', 15)
        self.speed_slider.setValue(last_position)
        self.update_speed()
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)

        self.transpose_button = QPushButton("Transponer")
        self.transpose_button.clicked.connect(self.show_transpose_menu)
        control_layout.addWidget(self.transpose_button)
        
        # Añadir etiqueta para mostrar la codificación
        self.encoding_label = QLabel("Codificación: UTF-8")
        self.encoding_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.encoding_label)

        self.create_menu_bar()

        # Crear atajos de teclado
        find_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        find_shortcut.activated.connect(self.show_find_replace_dialog)
        
        replace_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        replace_shortcut.activated.connect(self.show_find_replace_dialog)
        
        scroll_shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        scroll_shortcut.activated.connect(self.toggle_scroll)

        self.tab_widget.currentChanged.connect(self.update_encoding_label)
        self.setAcceptDrops(True)

    def show_find_replace_dialog(self):
        if not self.find_replace_dialog:
            self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
        self.find_replace_dialog.find_input.setFocus()

    def update_encoding_label(self, index):
        print(f"Actualizando etiqueta para la pestaña {index}")
        file_path = self.opened_files.get(index, None)
        if file_path and file_path in self.file_encodings:
            encoding = self.file_encodings[file_path]['encoding']
            line_ending = self.file_encodings[file_path]['line_ending']
            self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")
            self.setWindowTitle(f"{os.path.basename(file_path)} - Lector y Editor de Texto con acordes")
        else:
            self.encoding_label.setText("Codificación: N/A | Terminador de línea: N/A")
            self.setWindowTitle("Lector y Editor de Texto con acordes")

    def toggle_scroll(self):
        if self.is_scrolling:
            self.pause_scrolling()
        else:
            self.start_scrolling()

    def add_new_tab(self, file_name=None, content="", file_path=None):
        text_widget = CustomTextEdit()
        text_widget.setUndoRedoEnabled(True)
        text_widget.document().setModified(False)
        text_widget.textChanged.connect(self.on_text_changed)

        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        text_widget.setFont(QFont(default_font, default_font_size))

        if content:
            text_widget.setPlainText(content)
            text_widget.document().setModified(False)

        tab_name = file_name if file_name else "Nuevo archivo"
        index = self.tab_widget.addTab(text_widget, tab_name)

        if file_path:
            self.opened_files[index] = file_path
        else:
            self.opened_files[index] = None

        self.tab_widget.setCurrentWidget(text_widget)
        self.update_window_title()

    def on_text_changed(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_index = self.tab_widget.currentIndex()
            file_path = self.opened_files.get(current_index, None)

            if file_path:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        saved_content = f.read()
                except Exception as e:
                    saved_content = ""

                current_content = current_widget.toPlainText()
                is_modified = current_content != saved_content
                current_widget.document().setModified(is_modified)
                self.update_window_title()

    def update_window_title(self):
        current_index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(current_index, "Nuevo archivo")
        file_name = os.path.basename(file_path) if file_path else "Nuevo archivo"
        modified = "*" if self.get_current_text_widget().document().isModified() else ""
        self.setWindowTitle(f"{file_name} {modified} - Lector y Editor de Letras con Acordes")

    def close_tab(self, index):
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
            reply = QMessageBox.question(
                self, "Cerrar documento",
                f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                "¿Desea guardar los cambios, o descartarlos?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.tab_widget.setCurrentIndex(index)
                self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return

        self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        for index in range(self.tab_widget.count()):
            self.tab_widget.setCurrentIndex(index)
            current_widget = self.tab_widget.widget(index)
            if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
                reply = QMessageBox.question(
                    self, "Cerrar aplicación",
                    f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                    "¿Desea guardar los cambios, o descartarlos?",
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return

        event.accept()

    def get_current_text_widget(self):
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, CustomTextEdit):
            return widget
        return None

    def copy_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.copy()

    def paste_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.paste()

    def cut_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.cut()

    def change_spell_language(self):
        languages = {
            'Español': 'es',
            'English': 'en_US',
            'Deutsch': 'de_DE'
        }
        
        language_name, ok = QInputDialog.getItem(
            self, "Idioma del corrector",
            "Seleccione el idioma:",
            list(languages.keys()),
            0,
            False
        )
        
        if ok:
            language_code = languages[language_name]
            current_widget = self.get_current_text_widget()
            if current_widget:
                current_widget.set_spell_language(language_code)

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")

        new_action = QAction("Nuevo archivo", self)
        new_action.triggered.connect(self.add_new_tab)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)

        recent_menu = file_menu.addMenu("Abrir reciente")
        self.recent_menu = recent_menu

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar como", self)
        save_as_action.triggered.connect(self.save_file_as_original)
        save_as_action.setShortcut("Ctrl+Shift+S")
        file_menu.addAction(save_as_action)

        save_as_encoding_action = QAction("Guardar Codificación como...", self)
        save_as_encoding_action.triggered.connect(self.save_file_with_encoding)
        file_menu.addAction(save_as_encoding_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        # Menú Editar
        edit_menu = menu_bar.addMenu("Editar")

        undo_action = QAction("Deshacer", self)
        undo_action.triggered.connect(lambda: self.get_current_text_widget().undo())
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.triggered.connect(lambda: self.get_current_text_widget().redo())
        redo_action.setShortcut("Ctrl+Shift+Z")
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copy_text)
        copy_action.setShortcut("Ctrl+C")
        edit_menu.addAction(copy_action)

        paste_action = QAction("Pegar", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("Ctrl+V")
        edit_menu.addAction(paste_action)

        cut_action = QAction("Cortar", self)
        cut_action.triggered.connect(self.cut_text)
        cut_action.setShortcut("Ctrl+X")
        edit_menu.addAction(cut_action)

        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(lambda: self.get_current_text_widget().selectAll())
        select_all_action.setShortcut("Ctrl+A")
        edit_menu.addAction(select_all_action)

        edit_menu.addSeparator()

        # Nuevas opciones de búsqueda
        find_action = QAction("Buscar", self)
        find_action.triggered.connect(self.show_find_replace_dialog)
        find_action.setShortcut("Ctrl+F")
        edit_menu.addAction(find_action)

        replace_action = QAction("Buscar y reemplazar", self)
        replace_action.triggered.connect(self.show_find_replace_dialog)
        replace_action.setShortcut("Ctrl+H")
        edit_menu.addAction(replace_action)

        # Menú Herramientas
        tools_menu = menu_bar.addMenu("Herramientas")

        spell_language_action = QAction("Cambiar idioma del corrector", self)
        spell_language_action.triggered.connect(self.change_spell_language)
        tools_menu.addAction(spell_language_action)

        # Menú Opciones
        options_menu = menu_bar.addMenu("Opciones")

        sharps_action = QAction("Usar Sostenidos al bajar semitonos", self)
        sharps_action.setCheckable(True)
        sharps_action.setChecked(self.config.get('use_sharps', True))
        sharps_action.triggered.connect(lambda: self.toggle_accidentals(True))
        options_menu.addAction(sharps_action)

        flats_action = QAction("Usar Bemoles al bajar semitonos", self)
        flats_action.setCheckable(True)
        flats_action.setChecked(not self.config.get('use_sharps', True))
        flats_action.triggered.connect(lambda: self.toggle_accidentals(False))
        options_menu.addAction(flats_action)

        options_menu.addSeparator()

        group = QActionGroup(self)
        group.addAction(sharps_action)
        group.addAction(flats_action)

        change_font_action = QAction("Cambiar fuente", self)
        change_font_action.triggered.connect(self.select_font)
        options_menu.addAction(change_font_action)

        change_speed_action = QAction("Cambiar velocidad máxima", self)
        change_speed_action.triggered.connect(self.change_max_speed)
        change_speed_action.setShortcut("Ctrl+Shift+V")
        options_menu.addAction(change_speed_action)

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")

        about_action = QAction("Acerca de...", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setShortcut("Ctrl+I")
        help_menu.addAction(about_action)

    def select_font(self):
        font, ok = QFontDialog.getFont(QFont(self.config.get('font_family', 'Noto Mono'),
                                            self.config.get('font_size', 10)),
                                    self, "Selecciona una fuente")
        if ok:
            current_widget = self.get_current_text_widget()
            if current_widget:
                current_widget.setFont(font)
            self.config['font_family'] = font.family()
            self.config['font_size'] = font.pointSize()
            self.save_config()

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        recent_files = self.config.get('recent_files', [])

        for entry in recent_files:
            file_path = entry['path']
            timestamp = entry['timestamp']
            action = QAction(f"{os.path.basename(file_path)} - {timestamp}", self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_menu.addAction(action)

            path_action = QAction(f"Ruta: {file_path}", self)
            path_action.setEnabled(False)
            self.recent_menu.addAction(path_action)

        if not recent_files:
            self.recent_menu.addAction("No hay archivos recientes").setEnabled(False)

    def open_recent_file(self, file_path):
        if os.path.exists(file_path):
            self.open_dropped_file(file_path)
        else:
            QMessageBox.warning(self, "Error", f"El archivo '{file_path}' no existe.")

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
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'

                if b'\r\n' in raw_data:
                    line_ending = "Windows (CRLF)"
                elif b'\n' in raw_data:
                    line_ending = "Unix (LF)"
                elif b'\r' in raw_data:
                    line_ending = "Mac (CR)"
                else:
                    line_ending = "Desconocido"

                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()

                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")

                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content, file_path=file_path)

                self.config['last_opened_path'] = os.path.dirname(file_path)
                self.save_config()
                self.update_window_title()
                self.add_to_recent_files(file_path)

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

    def add_to_recent_files(self, file_path):
        from datetime import datetime
        recent_files = self.config.get('recent_files', [])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        recent_files = [f for f in recent_files if f['path'] != file_path]
        recent_files.insert(0, {'path': file_path, 'timestamp': timestamp})
        self.config['recent_files'] = recent_files[:9]
        self.save_config()
        self.update_recent_files_menu()

    def open_file(self):
        last_path = self.config.get('last_opened_path', '')
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", last_path, "Archivos de texto (*.txt)")
        if file_path:
            self.open_dropped_file(file_path)

    def save_file(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(index)

        if file_path:
            try:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')
                line_ending = self.file_encodings.get(file_path, {}).get('line_ending', 'Unix (LF)')
                content = current_widget.toPlainText()
                
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)
                    
                current_widget.document().setModified(False)
                self.update_window_title()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            self.save_file_as_original()

    def save_file_as_original(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)")
        
        if file_path:
            try:
                encoding = self.file_encodings.get(suggested_name, {}).get('encoding', 'utf-8')
                line_ending = self.file_encodings.get(suggested_name, {}).get('line_ending', 'Unix (LF)')
                content = current_widget.toPlainText()
                
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)

                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                self.tab_widget.setTabText(index, os.path.basename(file_path))
                current_widget.document().setModified(False)
                self.update_window_title()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

    def save_file_with_encoding(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)")
        
        if file_path:
            encoding, ok = QInputDialog.getItem(
                self, "Seleccionar codificación", "Codificación:",
                ["UTF-8", "UTF-16 LE", "UTF-16 BE", "UTF-8 con BOM", "ANSI", "ISO-8859-1"],
                0, False
            )
            if not ok:
                return

            line_ending, ok = QInputDialog.getItem(
                self, "Seleccionar terminador de línea", "Terminador de línea:",
                ["Windows (CRLF)", "Unix (LF)", "Mac (CR)"],
                0, False
            )
            if not ok:
                return

            try:
                content = current_widget.toPlainText()
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                if encoding == "UTF-8 con BOM":
                    with open(file_path, 'w', encoding='utf-8-sig') as file:
                        file.write(content)
                elif encoding == "ANSI":
                    with open(file_path, 'w', encoding='windows-1252') as file:
                        file.write(content)
                else:
                    with open(file_path, 'w', encoding=encoding.lower().replace(" ", "-")) as file:
                        file.write(content)

                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                self.tab_widget.setTabText(index, os.path.basename(file_path))
                current_widget.document().setModified(False)
                self.update_window_title()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

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
                                    f"La velocidad máxima se ha actualizado a {self.max_speed}.")

    def show_transpose_menu(self):
        transpose_menu = QMenu(self)
        for i in range(-7, 8):
            action = QAction(f"{i:+d}" if i != 0 else "0 (Original)", self)
            action.triggered.connect(lambda checked, x=i: self.transpose_chords(x))
            transpose_menu.addAction(action)
        transpose_menu.exec(self.transpose_button.mapToGlobal(self.transpose_button.rect().bottomLeft()))

    def transpose_chords(self, semitones):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_scroll_position = current_widget.verticalScrollBar().value()
            content = current_widget.toPlainText()
            transposed_content = self.transpose_text(content, semitones)
            
            cursor = current_widget.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.insertText(transposed_content)
            cursor.endEditBlock()
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
            new_root = chord_base[new_index][0] if self.config.get('use_sharps', True) else chord_base[new_index][-1]
            return new_root + suffix, ' ' * spaces_after

        def is_chord_line(line):
            words = line.split()
            matches = [bool(re.fullmatch(chord_pattern, word)) for word in words]
            return sum(matches) > len(words) / 2

        def process_line(line):
            chord_positions = list(re.finditer(chord_pattern, line))
            if not chord_positions:
                return line

            new_line = []
            last_end = 0

            for i, match in enumerate(chord_positions):
                new_line.append(line[last_end:match.start()])
                next_pos = chord_positions[i + 1].start() if i + 1 < len(chord_positions) else len(line)
                spaces_after = next_pos - match.end()
                new_chord, new_spaces = transpose_chord(match.group(), spaces_after)
                new_line.append(new_chord + new_spaces)
                last_end = next_pos

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
                'font_family': 'Noto Mono',
                'font_size': 10,
                'last_opened_path': '',
                'use_sharps': True
            }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def toggle_accidentals(self, use_sharps):
        self.config['use_sharps'] = use_sharps
        self.save_config()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())

