import os
import tkinter as tk
from tkinter import TclError

class TkDND:
    def __init__(self, master):
        # Inicializa la funcionalidad de arrastrar y soltar
        self.master = master
        self.tk = master.tk
        self._load_tkdnd_package()

    def _load_tkdnd_package(self):
        # Intenta cargar el paquete tkdnd
        try:
            self.tk.call('package', 'require', 'tkdnd')
        except TclError:
            # Si falla, busca la librería manualmente y cárgala
            dndlib = self._find_tkdnd_library()
            if dndlib:
                self.tk.call('load', dndlib, 'tkdnd')
                self.tk.call('package', 'require', 'tkdnd')
            else:
                raise RuntimeError('Cannot find tkdnd library.')

    def _find_tkdnd_library(self):
        # Intenta encontrar la librería tkdnd en el sistema
        tk_version = self.tk.eval('info patchlevel')
        platform = self.tk.eval('tk windowingsystem')
        lib_name = f'tkdnd{tk_version.split(".")[0]}{platform}.so'
        search_paths = [
            os.path.join(os.path.dirname(__file__), 'lib'),
            os.path.join(os.path.dirname(__file__), '..', 'lib'),
            os.path.join(os.path.dirname(__file__), 'ext')
        ]
        for path in search_paths:
            lib_path = os.path.join(path, lib_name)
            if os.path.exists(lib_path):
                return lib_path
        return None

    def bindtarget(self, widget, type_list, event='<Drop>', func=None, priority=None):
        # Vincula un widget como destino de arrastre y soltado
        widget.tk.call('dnd', 'bindtarget', widget, type_list, event, func, priority)

    def bindsource(self, widget, type_list, priority=None):
        # Vincula un widget como fuente de arrastre y soltado
        widget.tk.call('dnd', 'bindsource', widget, type_list, priority)


if __name__ == '__main__':
    root = tk.Tk()
    dnd = TkDND(root)

    # Ejemplo de uso: un área de texto que acepta texto arrastrado
    text = tk.Text(root)
    text.pack()

    def on_drop(event):
        text.insert(tk.END, event.data)

    dnd.bindtarget(text, '*', '<Drop>', on_drop)

    root.mainloop()
