### Instrucciones

1. **Instalación de Tkinter**: Asegúrate de tener Tkinter instalado en tu sistema. En la mayoría de las distribuciones de Linux, viene preinstalado, pero puedes instalarlo con:

   ```sh
   sudo apt-get install python3-tk tk-dev python3 python3-pyqt6 tkdnd python3-mpmath python3-simplejson python3-all-dev python3-pyqt5 fonts-noto-mono
   ```


2. **Ejecutar el script**: Para abrir la interfaz de usuario ejecuta el script en una terminal con:

   ```sh
   python3 chord_autoscroll.py
   ```

Abre un archivo de acordes como los que están aquí.

### Cambios principales en esta versión:

Se ha añadido una nueva función **calculate_speed** que utiliza una función exponencial para calcular la velocidad:

   ```sh
pythonCopydef calculate_speed(self, value):
    min_speed = 320
    max_speed = 6400
    factor = math.log(max_speed / min_speed) / 29
    return int(min_speed * math.exp(factor * (30 - value)))
   ```
   
La función **update_speed** ahora utiliza calculate_speed:

   ```sh
pythonCopydef update_speed(self, value):
    self.scroll_speed = self.calculate_speed(float(value))
   ```
   
La velocidad por defecto ahora se calcula utilizando la nueva función:

   ```sh
pythonCopyself.scroll_speed = self.calculate_speed(15)  # Velocidad por defecto
   ```
   
Con estos cambios:

La velocidad más lenta sigue siendo de 6400ms (cuando el valor de la escala es 1).
La velocidad más rápida sigue siendo de 320ms (cuando el valor de la escala es 30).
El cambio entre estas velocidades ahora es progresivo y suave, siguiendo una curva exponencial.

Esta implementación proporciona una transición más natural entre las velocidades, con cambios más pequeños en las velocidades más lentas y cambios más grandes en las velocidades más rápidas. Esto debería dar una sensación más intuitiva al ajustar la velocidad.






# ME sale este error:

Me sale este error:

```bash
$ python3 chord_autoscroll.py
Traceback (most recent call last):
  File "/home/wachin/Dev-python/py_chord_autoscroll/chord_autoscroll_v20_usando-fuente-noto-mono-por-defecto.py", line 326, in <module>
    window = TextScrollerApp()
             ^^^^^^^^^^^^^^^^^
  File "/home/wachin/Dev-python/py_chord_autoscroll/chord_autoscroll_v20_usando-fuente-noto-mono-por-defecto.py", line 32, in __init__
    self.init_ui()
  File "/home/wachin/Dev-python/py_chord_autoscroll/chord_autoscroll_v20_usando-fuente-noto-mono-por-defecto.py", line 58, in init_ui
    default_font = self.config.get('font_family', 'Noto Mono')
                   ^^^^^^^^^^^
AttributeError: 'TextScrollerApp' object has no attribute 'config'
```

aquí envio los cambios que hice:

```python
import sys
import os
import math
import re
import json
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox, QInputDialog, QFontDialog)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Desactivar el manejo de drops por defecto

class TextScrollerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lector y Editor de Texto")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 100  # Velocidad máxima predeterminada
        self.scroll_speed = self.calculate_speed(15)  # Velocidad predeterminada

        self.config_file = 'config.json'
        self.load_config()

        self.init_ui()

    def select_font(self):
        # Abrir diálogo de selección de fuente
        font, ok = QFontDialog.getFont(QFont(self.config.get('font_family', 'Noto Mono'),
                                            self.config.get('font_size', 10)),
                                    self, "Selecciona una fuente")

        # Si el usuario selecciona una fuente y presiona OK
        if ok:
            # Aplicar la fuente seleccionada al área de texto
            self.text_widget.setFont(font)

            # Guardar la fuente seleccionada en la configuración
            self.config['font_family'] = font.family()
            self.config['font_size'] = font.pointSize()
            self.save_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.text_widget = CustomTextEdit()

        # Aplicar la fuente predeterminada desde la configuración
        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        self.text_widget.setFont(QFont(default_font, default_font_size))

        layout.addWidget(self.text_widget)

        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_scrolling)
        control_layout.addWidget(self.start_button)
    # El resto del codigo igual
```
