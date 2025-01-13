    def on_text_changed(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_index = self.tab_widget.currentIndex()
            file_path = self.opened_files.get(current_index, None)

            # Verificar que el archivo exista en la lista de archivos abiertos
            if file_path:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')  # Obtener la codificación

                try:
                    # Leer el contenido guardado del archivo
                    with open(file_path, 'r', encoding=encoding) as f:
                        saved_content = f.read()
                except Exception as e:
                    saved_content = ""  # Si ocurre un error al leer, asumir contenido vacío

                # Obtener el contenido actual del widget
                current_content = current_widget.toPlainText()

                # Comparar ambos para verificar si realmente ha sido modificado
                is_modified = current_content != saved_content
                current_widget.document().setModified(is_modified)

                # Actualizar el título de la ventana
                self.update_window_title()

