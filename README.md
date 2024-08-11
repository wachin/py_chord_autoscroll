### Instrucciones

1. **Instalación de Tkinter**: Asegúrate de tener Tkinter instalado en tu sistema. En la mayoría de las distribuciones de Linux, viene preinstalado, pero puedes instalarlo con:

   ```sh
   sudo apt-get install python3-pyqt6
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

