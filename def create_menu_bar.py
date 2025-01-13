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

        # Menú Abrir reciente
        recent_menu = file_menu.addMenu("Abrir reciente")
        self.recent_menu = recent_menu  # Guardar referencia al menú para actualizarlo

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")  # Atajo: Ctrl+S
        file_menu.addAction(save_action)

        # Opción Guardar como
        save_as_action = QAction("Guardar como...", self)
        save_as_action.triggered.connect(self.save_file_as)  # Llama a save_file_as en lugar de save_file
        save_as_action.setShortcut("Ctrl+Shift+S")  # Atajo: Ctrl+Shift+S
        file_menu.addAction(save_as_action)

        # Opción Guardar Codificación como
        save_as_encoding_action = QAction("Guardar Codificación como...", self)
        save_as_encoding_action.triggered.connect(self.save_file_with_encoding)
        file_menu.addAction(save_as_encoding_action)

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

        # Añadir un separador
        edit_menu.addSeparator()

        # Nueva opción: Copiar
        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copy_text)
        copy_action.setShortcut("Ctrl+C")  # Atajo de teclado: Ctrl+C
        edit_menu.addAction(copy_action)

        # Nueva opción: Pegar
        paste_action = QAction("Pegar", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("Ctrl+V")  # Atajo de teclado: Ctrl+V
        edit_menu.addAction(paste_action)

        # Nueva opción: Cortar

        cut_action = QAction("Cortar", self)
        cut_action.triggered.connect(self.cut_text)
        cut_action.setShortcut("Ctrl+X")  # Atajo de teclado: Ctrl+X
        edit_menu.addAction(cut_action)

        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(lambda: self.get_current_text_widget().selectAll())
        select_all_action.setShortcut("Ctrl+A")  # Atajo: Ctrl+A
        edit_menu.addAction(select_all_action)

        # Menú Opciones
        options_menu = menu_bar.addMenu("Opciones")

        # Opción para usar sostenidos
        sharps_action = QAction("Usar Sostenidos al bajar semitonos", self)
        sharps_action.setCheckable(True)
        sharps_action.setChecked(self.config['use_sharps'])
        sharps_action.triggered.connect(lambda: self.toggle_accidentals(True))
        options_menu.addAction(sharps_action)

        # Opción para usar bemoles
        flats_action = QAction("Usar Bemoles al bajar semitonos", self)
        flats_action.setCheckable(True)
        flats_action.setChecked(not self.config['use_sharps'])
        flats_action.triggered.connect(lambda: self.toggle_accidentals(False))
        options_menu.addAction(flats_action)

        # Añadir un separador
        options_menu.addSeparator()

        # Agrupar las opciones para que sean mutuamente excluyentes
        group = QActionGroup(self)
        group.addAction(sharps_action)
        group.addAction(flats_action)

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
