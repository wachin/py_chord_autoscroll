import tkinter as tk
from tkinter import filedialog, messagebox
import math
import re
import os
import tkinter.dnd as dnd

class TextScrollerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lector y Editor de Texto")
        self.master.geometry("800x500")

        self.current_file = None

        self.text_widget = tk.Text(self.master, wrap=tk.WORD)
        self.text_widget.pack(expand=True, fill='both')

        self.scrollbar = tk.Scrollbar(self.text_widget)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.text_widget.yview)

        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Salir", command=self.master.quit)

        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(fill=tk.X)

        self.start_button = tk.Button(self.control_frame, text="Iniciar", command=self.start_scrolling)
        self.start_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.control_frame, text="Pausar", command=self.pause_scrolling)
        self.pause_button.pack(side=tk.LEFT)

        self.speed_label = tk.Label(self.control_frame, text="Velocidad:")
        self.speed_label.pack(side=tk.LEFT)

        self.speed_scale = tk.Scale(self.control_frame, from_=1, to=30, orient=tk.HORIZONTAL, command=self.update_speed, length=300)
        self.speed_scale.set(15)  # Valor medio por defecto
        self.speed_scale.pack(side=tk.LEFT)

        self.transpose_button = tk.Button(self.control_frame, text="Transponer", command=self.show_transpose_menu)
        self.transpose_button.pack(side=tk.LEFT)

        self.is_scrolling = False
        self.scroll_speed = self.calculate_speed(15)  # Velocidad por defecto

        # Configurar drag and drop
        dnd.dnd_start(self.master, self.drop_file)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")], 
                                               initialdir=os.path.expanduser("~"))
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            self.text_widget.delete('1.0', tk.END)
            self.text_widget.insert(tk.END, content)
        self.current_file = file_path
        self.master.title(f"Lector y Editor de Texto - {os.path.basename(file_path)}")

    def save_file(self):
        if self.current_file:
            content = self.text_widget.get('1.0', tk.END)
            with open(self.current_file, 'w') as file:
                file.write(content)
            messagebox.showinfo("Guardado", "Archivo guardado exitosamente.")
        else:
            self.save_file_as()

    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if file_path:
            content = self.text_widget.get('1.0', tk.END)
            with open(file_path, 'w') as file:
                file.write(content)
            self.current_file = file_path
            self.master.title(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
            messagebox.showinfo("Guardado", "Archivo guardado exitosamente.")

    def drop_file(self, event):
        file_path = event.data
        if file_path.endswith('.txt'):
            self.load_file(file_path)
        else:
            messagebox.showwarning("Formato no soportado", "Solo se aceptan archivos .txt")

    def start_scrolling(self):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_text()

    def pause_scrolling(self):
        self.is_scrolling = False

    def scroll_text(self):
        if self.is_scrolling:
            self.text_widget.yview_scroll(1, 'units')
            self.master.after(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        min_speed = 320
        max_speed = 6400
        factor = math.log(max_speed / min_speed) / 29
        return int(min_speed * math.exp(factor * (30 - value)))

    def update_speed(self, value):
        self.scroll_speed = self.calculate_speed(float(value))

    def show_transpose_menu(self):
        transpose_menu = tk.Menu(self.master, tearoff=0)
        for i in range(-7, 8):
            if i == 0:
                transpose_menu.add_command(label="0 (Original)", command=lambda x=i: self.transpose_chords(x))
            else:
                transpose_menu.add_command(label=f"{i:+d}", command=lambda x=i: self.transpose_chords(x))
        transpose_menu.post(self.transpose_button.winfo_rootx(), self.transpose_button.winfo_rooty() + self.transpose_button.winfo_height())

    def transpose_chords(self, semitones):
        content = self.text_widget.get('1.0', tk.END)
        transposed_content = self.transpose_text(content, semitones)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, transposed_content)

    def transpose_text(self, text, semitones):
        chord_pattern = r'\b[A-G](#|b)?(m|dim|dim7|aug|maj|min|sus|bm|add)?[0-9]?(?:\s|$)'
        
        def transpose_chord(match):
            chord = match.group(0)
            root = chord[0]
            sharp_flat = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + sharp_flat):]

            notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            index = notes.index(root + sharp_flat) if root + sharp_flat in notes else notes.index(root)
            new_index = (index + semitones) % 12
            new_root = notes[new_index]

            return new_root + suffix

        return re.sub(chord_pattern, transpose_chord, text)

if __name__ == "__main__":
    root = tk.Tk()
    app = TextScrollerApp(root)
    root.mainloop()
