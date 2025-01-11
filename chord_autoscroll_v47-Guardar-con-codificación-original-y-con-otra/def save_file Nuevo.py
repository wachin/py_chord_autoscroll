    def save_file(self):
        current_index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(current_index, None)

        if file_path:
            current_widget = self.get_current_text_widget()
            if current_widget:
                content = current_widget.toPlainText()
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')

                try:
                    with open(file_path, 'w', encoding=encoding) as f:
                        f.write(content)
                    current_widget.document().setModified(False)
                    self.update_window_title()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
