    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")

        # Opción Guardar
        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)

        # Opción Guardar como
        save_as_action = QAction("Guardar como...", self)
        save_as_action.triggered.connect(self.save_file_as_original)
        file_menu.addAction(save_as_action)

        # Opción Guardar Codificación como
        save_as_encoding_action = QAction("Guardar Codificación como...", self)
        save_as_encoding_action.triggered.connect(self.save_file_with_encoding)
        file_menu.addAction(save_as_encoding_action)

        # Opción Salir
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
