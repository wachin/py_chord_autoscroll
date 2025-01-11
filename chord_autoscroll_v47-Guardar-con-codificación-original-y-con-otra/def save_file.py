    def save_file(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(index)

        if file_path:
            # Guardar directamente en la ubicación conocida
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(current_widget.toPlainText())
                # Desabilito el mensaje de configuración al guardar cualquier archivo
                # QMessageBox.information(self, "Guardado", f"Archivo guardado en {file_path}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            # Si no hay ubicación conocida, mostrar "Guardar como"
            self.save_file_as()

        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.document().setModified(False)  # Marcar como no modificado
            self.update_window_title()  # Actualizar el título
