    def on_text_changed(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_index = self.tab_widget.currentIndex()
            file_path = self.opened_files.get(current_index)
            encoding = self.file_encodings.get(file_path, 'utf-8')  # Usar codificación detectada o UTF-8

            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    saved_text = f.read()
            except Exception as e:
                saved_text = ""  # Si ocurre un error, asumir que el archivo está vacío

            # Comparar el texto actual con el texto guardado
            current_text = current_widget.toPlainText()
            is_modified = current_text != saved_text
            current_widget.document().setModified(is_modified)

            # Actualizar el título de la ventana
            self.update_window_title()
