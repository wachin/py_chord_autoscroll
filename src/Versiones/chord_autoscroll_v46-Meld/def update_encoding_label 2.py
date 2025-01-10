    def update_encoding_label(self, index):
        file_path = self.opened_files.get(index, None)
        if file_path and isinstance(self.file_encodings.get(file_path), dict):
            encoding = self.file_encodings[file_path].get('encoding', 'N/A')
            line_ending = self.file_encodings[file_path].get('line_ending', 'N/A')
            self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")
        else:
            self.encoding_label.setText("Codificación: N/A | Terminador de línea: N/A")
