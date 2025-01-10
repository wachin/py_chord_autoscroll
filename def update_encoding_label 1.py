    def update_encoding_label(self, index):
        file_path = self.opened_files.get(index, None)
        if file_path and file_path in self.file_encodings:
            encoding = self.file_encodings[file_path]['encoding']
            line_ending = self.file_encodings[file_path]['line_ending']
            self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")
        else:
            self.encoding_label.setText("Codificación: N/A | Terminador de línea: N/A")
