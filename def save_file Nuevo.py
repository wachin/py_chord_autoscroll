    def save_file(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(index)

        if file_path:
            # Guardar directamente en la ubicación conocida con la codificación y fin de línea originales
            try:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')
                line_ending = self.file_encodings.get(file_path, {}).get('line_ending', 'Unix (LF)')

                # Obtener el contenido y ajustar el fin de línea
                content = current_widget.toPlainText()
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            self.save_file_as()

        current_widget.document().setModified(False)  # Marcar como no modificado
        self.update_window_title()
