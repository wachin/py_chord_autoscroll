    def open_file(self):
        # Obtener la última ruta desde la configuración
        last_path = self.config.get('last_opened_path', '')

        # Abrir el cuadro de diálogo de selección de archivo, iniciando en la última ruta
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", last_path, "Archivos de texto (*.txt)")
        if file_path:
            try:
                # Detectar la codificación del archivo
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'

                # Detectar el tipo de terminador de línea en modo binario
                if b'\r\n' in raw_data:
                    line_ending = "Windows (CRLF)"
                elif b'\n' in raw_data:
                    line_ending = "Unix (LF)"
                elif b'\r' in raw_data:
                    line_ending = "Mac (CR)"
                else:
                    line_ending = "Desconocido"

                # Guardar la codificación y el terminador de línea
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}

                # Actualizar la etiqueta de codificación y terminador de línea
                self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")

                # Leer el archivo con la codificación detectada
                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()

                # Cargar el contenido en la pestaña actual o abrir una nueva
                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content, file_path=file_path)

                # Guardar la última ruta en la configuración
                self.config['last_opened_path'] = os.path.dirname(file_path)
                self.save_config()  # Guardar la configuración actualizada

                # Actualizar el título de la ventana
                self.update_window_title()

                # Añadir a la lista de archivos recientes
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")
