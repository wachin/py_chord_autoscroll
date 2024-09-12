### Manual de Instalación y Uso del Programa para Guitarristas en Linux Debian 12, MX Linux 23

Este manual está diseñado para guiar a guitarristas en la instalación y uso del programa de auto-scroll y transposición de acordes en Linux Debian 12, MX Linux 23. Con este programa, podrás cargar tus canciones con acordes, transportarlos fácilmente y desplazarte automáticamente por el texto, ¡perfecto para tus ensayos!

**Nota:** Es posible funcione en Ubuntu 24.04, Linux Mint y otros.

---

## **Instrucciones de Instalación**

### 1. **Instalación de dependencias**
Antes de ejecutar el programa, necesitas asegurarte de que ciertos paquetes estén instalados en tu sistema. Ejecuta el siguiente comando en la terminal para instalar las dependencias necesarias:

```bash
sudo apt-get install python3-tk tk-dev python3 python3-pyqt6 tkdnd python3-mpmath python3-simplejson python3-all-dev fonts-noto-mono
```

### 2. **Ejecutar el script**
Una vez instaladas las dependencias, puedes ejecutar el programa desde la terminal. Navega a la carpeta donde se encuentra el archivo `chord_autoscroll.py` y usa el siguiente comando:

```bash
python3 chord_autoscroll.py
```

---

## **Modo de Uso**

### 1. **Abrir canciones**
Existen dos maneras de cargar tus archivos de texto con acordes en el programa:
- **Arrastrar y soltar archivos**: Simplemente arrastra un archivo de texto (con extensión `.txt`) hacia la ventana del programa.
- **Abrir desde el menú**: Haz clic en "Archivo > Abrir" en la barra de menú para seleccionar y cargar tus archivos.

**Ejemplos de archivos incluidos:**
- *Eres Todopoderoso (Bm).txt*
- *La niña de tus ojos - Daniel Calveti (C).txt*
- *Sana nuestra tierra - Marcos W. (F).txt*
- *Sananos - Marcos W. (D).txt*

### 2. **Transponer acordes**
El programa cuenta con un botón **"Transponer"**, ubicado en la esquina inferior derecha. Al hacer clic, se abrirá un menú donde puedes ajustar los semitonos de tus acordes:
- **Subir semitonos**: Desplázate hacia arriba para aumentar el tono.
- **Bajar semitonos**: Desplázate hacia abajo para reducir el tono.

Esto es especialmente útil cuando necesitas adaptar una canción a tu voz o a la afinación de tu guitarra.

### 3. **Control de desplazamiento**
El programa te permite desplazarte automáticamente por la letra y acordes de la canción, facilitando la lectura durante la interpretación.

- **Iniciar/Pausar desplazamiento**: Usa los botones **"Iniciar"** y **"Pausar"** para controlar el desplazamiento automático.
- **Ajustar velocidad**: Usa el deslizador de velocidad para ajustar la rapidez del desplazamiento según tu necesidad.

### 4. **Cambiar fuente**
El programa ofrece la posibilidad de personalizar la fuente de los acordes. En el menú "Opciones > Cambiar fuente", puedes seleccionar la fuente de tu preferencia. Por defecto, se utiliza una fuente monoespaciada **Noto Mono**, perfecta para asegurar la correcta alineación de los acordes.

---

## **Consideraciones Finales**
Este programa es ideal para guitarristas que necesitan gestionar archivos de canciones y ajustar los acordes rápidamente durante ensayos o presentaciones. Con características de auto-scroll y transposición, tendrás todas las herramientas necesarias a tu disposición.

Si tienes alguna dificultad o preguntas, puedes contactar al desarrollador.

---

### **Notas sobre las dependencias:**

Si encuentras que falta alguna dependencia en tu sistema, puedes agregarla mediante el comando `apt-get` de forma similar. El programa depende principalmente de **Python 3**, **PyQt6** y algunas bibliotecas adicionales para manejo de fuentes y archivos.
