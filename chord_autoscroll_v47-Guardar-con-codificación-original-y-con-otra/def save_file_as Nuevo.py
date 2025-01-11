    def save_file_as(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar como", "", "Archivos de texto (*.txt)")
            if file_path:
                # Diálogo para seleccionar codificación
                encoding, ok = QInputDialog.getItem(
                    self,
                    "Seleccionar codificación",
                    "Codificación:",
                    ["UTF-8", "UTF-16 LE", "UTF-16 BE", "UTF-8 con BOM"],
                    0,
                    False
                )
                if ok:
                    content = current_widget.toPlainText()

                    # Guardar el archivo con la codificación seleccionada
                    try:
                        # Manejar UTF-8 con BOM
                        if encoding == "UTF-8 con BOM":
                            with open(file_path, 'w', encoding='utf-8-sig') as f:
                                f.write(content)
                        else:
                            with open(file_path, 'w', encoding=encoding.lower().replace(" ", "-")) as f:
                                f.write(content)

                        # Actualizar datos del archivo
                        self.file_encodings[file_path] = {'encoding': encoding}
                        self.opened_files[self.tab_widget.currentIndex()] = file_path
                        current_widget.document().setModified(False)
                        self.update_window_title()
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
