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
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(current_widget.toPlainText())

                # Asociar la pestaña con la nueva ubicación
                self.opened_files[index] = file_path
                self.tab_widget.setTabText(index, os.path.basename(file_path))

                QMessageBox.information(self, "Guardado", f"Archivo guardado en {file_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.document().setModified(False)  # Marcar como no modificado
            self.update_window_title()  # Actualizar el título
