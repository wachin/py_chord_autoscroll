

1. Modificación de la velocidad de desplazamiento por defecto a 400ms (el doble de lento que antes que era 200):
   ```python
   self.scroll_speed = 400  # Velocidad por defecto (milisegundos)
   ```

2. Ajuste de la función `update_speed` para proporcionar un rango más lento de velocidades:
   ```python
   def update_speed(self, value):
       # Ajuste de la velocidad: 800ms (más lento) a 40ms (más rápido)
       self.scroll_speed = int(840 - int(value) * 40)
   ```

Caracteristiccas  de velocidad:
- La velocidad más lenta ahora es de 800ms entre cada desplazamiento (cuando el valor de la escala es 1).
- La velocidad más rápida ahora es de 40ms (cuando el valor de la escala es 20).
- La velocidad media (cuando el valor de la escala es 10) será de 440ms.




