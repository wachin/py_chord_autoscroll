from tkdnd import TkDND
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import enchant
from enchant.checker import SpellChecker
import json
import os

class AdvancedTextEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Editor de Texto Avanzado")
        self.master.geometry("800x600")

        self.filename = None
        self.text_modified = False
        self.config_file = 'config.json'
        try:
            self.load_config()
        except Exception as e:
            print(f"Error al cargar la configuración: {e}")
            self.config = {'speed': 50}

        self.create_widgets()
        self.create_menu()
        self.create_shortcuts()

        self.spell_checker = SpellChecker("es_ES")

        self.setup_drag_and_drop()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                print(f"Error al leer el archivo de configuración. Usando configuración por defecto.")
                self.config = {'speed': 50}
                self.save_config()  # Sobrescribe el archivo corrupto con la configuración por defecto
        else:
            self.config = {'speed': 50}
            self.save_config()  # Crea el archivo de configuración si no existe

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

    def create_widgets(self):
        # Área de texto principal
        self.text_area = tk.Text(self.master, wrap="word", undo=True)
        self.text_area.pack(expand=True, fill="both")

        # Barra de desplazamiento
        self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.text_area.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=self.scrollbar.set)

        # Barra de herramientas para el desplazamiento automático
        self.toolbar = ttk.Frame(self.master)
        self.toolbar.pack(side="bottom", fill="x")

        self.play_button = ttk.Button(self.toolbar, text="Play", command=self.start_autoscroll)
        self.play_button.pack(side="left")

        self.pause_button = ttk.Button(self.toolbar, text="Pause", command=self.pause_autoscroll)
        self.pause_button.pack(side="left")

        self.stop_button = ttk.Button(self.toolbar, text="Stop", command=self.stop_autoscroll)
        self.stop_button.pack(side="left")

        self.speed_scale = ttk.Scale(self.toolbar, from_=1, to=100, orient="horizontal", length=300,
                                     command=self.update_speed)
        self.speed_scale.set(self.config['speed'])
        self.speed_scale.pack(side="left", padx=10)

        # Botón para transportar acordes
        self.transpose_button = ttk.Button(self.toolbar, text="Transportar", command=self.show_transpose_menu)
        self.transpose_button.pack(side="right")

        # Variables para el autoscroll
        self.autoscroll_job = None
        self.autoscroll_speed = self.config['speed']

    def update_speed(self, event=None):
        self.autoscroll_speed = self.speed_scale.get()
        self.config['speed'] = self.autoscroll_speed
        self.save_config()

    def setup_drag_and_drop(self):
        try:
            self.master.tk.eval('package require tkdnd')
            self.text_area.dnd.bindtarget(self.text_area, 'text/uri-list')
            self.text_area.dnd_bind('<<Drop>>', self.drop_file)
        except tk.TclError as e:
            print(f"Error al configurar drag and drop: {e}")
            print("La funcionalidad de arrastrar y soltar no estará disponible.")

    def drop_file(self, event):
        file_path = event.data
        if file_path.startswith('{'):
            file_path = file_path[1:-1]  # Remove curly braces if present
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, file.read())
            self.filename = file_path
            self.text_modified = False

    def create_menu(self):
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Guardar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Guardar como", command=self.save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.master.quit)

        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Deshacer", command=self.text_area.edit_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rehacer", command=self.text_area.edit_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cortar", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Pegar", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Seleccionar todo", command=self.select_all, accelerator="Ctrl+A")

        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Verificar ortografía", command=self.check_spelling)

    def create_shortcuts(self):
        self.master.bind("<Control-n>", lambda event: self.new_file())
        self.master.bind("<Control-o>", lambda event: self.open_file())
        self.master.bind("<Control-s>", lambda event: self.save_file())
        self.master.bind("<Control-S>", lambda event: self.save_as())
        self.master.bind("<Control-x>", lambda event: self.cut_text())
        self.master.bind("<Control-c>", lambda event: self.copy_text())
        self.master.bind("<Control-v>", lambda event: self.paste_text())
        self.master.bind("<Control-a>", lambda event: self.select_all())

    def new_file(self):
        if self.text_modified:
            if messagebox.askyesno("Guardar cambios", "¿Desea guardar los cambios antes de crear un nuevo archivo?"):
                self.save_file()
        self.text_area.delete(1.0, tk.END)
        self.filename = None
        self.text_modified = False

    def open_file(self):
        if self.text_modified:
            if messagebox.askyesno("Guardar cambios", "¿Desea guardar los cambios antes de abrir un nuevo archivo?"):
                self.save_file()
        file = filedialog.askopenfile(parent=self.master, mode="r", title="Seleccione un archivo", filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file:
            contents = file.read()
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, contents)
            self.filename = file.name
            self.text_modified = False

    def save_file(self):
        if self.filename:
            contents = self.text_area.get(1.0, tk.END)
            with open(self.filename, "w") as file:
                file.write(contents)
            self.text_modified = False
        else:
            self.save_as()

    def save_as(self):
        file = filedialog.asksaveasfile(mode="w", defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file:
            contents = self.text_area.get(1.0, tk.END)
            file.write(contents)
            self.filename = file.name
            self.text_modified = False
            file.close()

    def cut_text(self):
        self.text_area.event_generate("<<Cut>>")

    def copy_text(self):
        self.text_area.event_generate("<<Copy>>")

    def paste_text(self):
        self.text_area.event_generate("<<Paste>>")

    def select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return "break"

    def check_spelling(self):
        content = self.text_area.get(1.0, tk.END)
        self.spell_checker.set_text(content)
        for error in self.spell_checker:
            self.text_area.tag_add("misspelled", f"1.0+{error.wordpos}c", f"1.0+{error.wordpos + len(error.word)}c")
        self.text_area.tag_config("misspelled", foreground="red", underline=True)

    def start_autoscroll(self):
        if self.autoscroll_job:
            self.master.after_cancel(self.autoscroll_job)
        self.autoscroll()

    def autoscroll(self):
        self.text_area.yview_scroll(1, "units")
        scroll_time = int(1000 / (self.autoscroll_speed / 10))  # Ajusta la velocidad
        self.autoscroll_job = self.master.after(scroll_time, self.autoscroll)

    def pause_autoscroll(self):
        if self.autoscroll_job:
            self.master.after_cancel(self.autoscroll_job)

    def stop_autoscroll(self):
        if self.autoscroll_job:
            self.master.after_cancel(self.autoscroll_job)
        self.text_area.yview_moveto(0)

    def show_transpose_menu(self):
        transpose_menu = tk.Menu(self.master, tearoff=0)
        for i in range(-7, 8):
            if i != 0:
                transpose_menu.add_command(label=f"{'+' if i > 0 else ''}{i}", command=lambda x=i: self.transpose_chords(x))
        transpose_menu.post(self.transpose_button.winfo_rootx(), self.transpose_button.winfo_rooty() + self.transpose_button.winfo_height())

    def transpose_chords(self, semitones):
        content = self.text_area.get(1.0, tk.END)
        transposed_content = self.transpose_text(content, semitones)
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, transposed_content)

    def transpose_text(self, text, semitones):
        chord_pattern = r'\b[A-G](#|b)?(m|dim|dim7|aug|maj|min|sus|bm|add)?[0-9]?(?:\s|$)'

        def transpose_chord(match):
            chord = match.group(0)
            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

            root = chord[0]
            sharp_flat = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + sharp_flat):]

            index = notes.index(root + sharp_flat) if root + sharp_flat in notes else notes.index(root)
            new_index = (index + semitones) % 12
            new_root = notes[new_index]

            return new_root + suffix + ' '

        return re.sub(chord_pattern, transpose_chord, text)

if __name__ == "__main__":
    root = tk.Tk()
    editor = AdvancedTextEditor(root)
    root.mainloop()
