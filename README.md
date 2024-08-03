### Instrucciones

1. **Instalación de Tkinter**: Asegúrate de tener Tkinter instalado en tu sistema. En la mayoría de las distribuciones de Linux, viene preinstalado, pero puedes instalarlo con:
   ```sh
   sudo apt-get install python3-tk
   ```

2. **Ejecutar el script**: Guarda el código en un archivo, por ejemplo, `app_manager.py`, y ejecuta el script con:
   ```sh
   python3 chord_autoscroll.py
   ```

Modificación de la velocidad de desplazamiento por defecto a 800ms (el doble de lento que antes 400ms):
   ```sh
pythonCopyself.scroll_speed = 800  # Velocidad por defecto (milisegundos)
   ```
   
Ajuste de la función update_speed para proporcionar un rango aún más lento de velocidades:
   ```sh
pythonCopydef update_speed(self, value):
    # Ajuste de la velocidad: 1600ms (más lento) a 80ms (más rápido)
    self.scroll_speed = int(1680 - int(value) * 80)
   ```

Con estos cambios:

La velocidad más lenta ahora es de 1600ms (1.6 segundos) entre cada desplazamiento (cuando el valor de la escala es 1).
La velocidad más rápida ahora es de 80ms (cuando el valor de la escala es 20).
La velocidad media (cuando el valor de la escala es 10) será de 880ms.

Esto hace que todo el rango de velocidades sea nuevamente la mitad de rápido que en la versión anterior. La velocidad más lenta es el doble de lenta que en la versión anterior, y la velocidad más rápida también es el doble de lenta que antes.



