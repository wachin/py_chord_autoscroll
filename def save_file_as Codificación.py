    def save_file_as(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        # Obtener el índice de la pestaña actual y el nombre del archivo asociado
        index = self.tab_widget.currentIndex()
        current_file_path = self.opened_files.get(index)
        suggested_name = current_file_path if current_file_path else "Nuevo archivo.txt"

        # Abrir el cuadro de diálogo de "Guardar como" con el nombre sugerido
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)")
        if file_path:
            # Seleccionar codificación
            encoding, ok = QInputDialog.getItem(
                self,
                "Seleccionar codificación",
                "Codificación:",
                ["UTF-8", "UTF-16 LE", "UTF-16 BE", "UTF-8 con BOM", "ANSI", "ISO-8859-1"],
                0,
                False
            )
            if ok:
                try:
                    # Obtener el contenido y ajustar el fin de línea
                    content = current_widget.toPlainText()
                    line_ending = self.file_encodings.get(file_path, {}).get('line_ending', 'Unix (LF)')
                    if line_ending == "Windows (CRLF)":
                        content = content.replace('\n', '\r\n')
                    elif line_ending == "Mac (CR)":
                        content = content.replace('\n', '\r')

                    # Guardar con la codificación seleccionada
                    if encoding == "UTF-8 con BOM":
                        with open(file_path, 'w', encoding='utf-8-sig') as file:
                            file.write(content)
                    elif encoding == "ANSI":
                        with open(file_path, 'w', encoding='windows-1252') as file:
                            file.write(content)
                    else:
                        with open(file_path, 'w', encoding=encoding.lower().replace(" ", "-")) as file:
                            file.write(content)

                    # Asociar la pestaña con la nueva ubicación y codificación
                    self.opened_files[index] = file_path
                    self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                    self.tab_widget.setTabText(index, os.path.basename(file_path))

                    QMessageBox.information(self, "Guardado", f"Archivo guardado en {file_path}.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

            current_widget.document().setModified(False)  # Marcar como no modificado
            self.update_window_title()
