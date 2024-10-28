import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import json
import os
import math
import re
from tkinter.scrolledtext import ScrolledText

class TextScrollerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lector y Editor de Texto")
        self.root.geometry("800x500")
        
        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 1700  # Velocidad máxima predeterminada
        self.scroll_speed = self.calculate_speed(15)  # Velocidad predeterminada
        
        self.config_file = 'config11.json'
        self.config = {}
        self.load_config()
        
        self.init_ui()
        
    def init_ui(self):
        # Crear menú
        self.create_menu_bar()
        
        # Área de texto principal
        self.text_widget = ScrolledText(self.root, wrap=tk.WORD)
        self.text_widget.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Aplicar la fuente predeterminada
        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        self.text_widget.configure(font=(default_font, default_font_size))
        
        # Frame para controles
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        # Botones y controles
        self.start_button = ttk.Button(control_frame, text="Iniciar", command=self.start_scrolling)
        self.start_button.pack(side='left', padx=2)
        
        self.pause_button = ttk.Button(control_frame, text="Pausar", command=self.pause_scrolling)
        self.pause_button.pack(side='left', padx=2)
        
        ttk.Label(control_frame, text="Velocidad:").pack(side='left', padx=2)
        
        self.speed_var = tk.IntVar(value=15)
        self.speed_slider = ttk.Scale(control_frame, from_=1, to=30, 
                                    variable=self.speed_var, orient='horizontal',
                                    command=self.update_speed)
        self.speed_slider.pack(side='left', padx=2, fill='x', expand=True)
        
        self.transpose_button = ttk.Button(control_frame, text="Transponer", 
                                         command=self.show_transpose_menu)
        self.transpose_button.pack(side='left', padx=2)
        
    def create_menu_bar(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Nuevo archivo", command=self.new_file)
        file_menu.add_command(label="Abrir", command=self.open_file)
        file_menu.add_command(label="Guardar", command=self.save_file)
        file_menu.add_command(label="Guardar como", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        
        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Seleccionar todo", 
                            command=lambda: self.text_widget.tag_add('sel', '1.0', 'end'))
        
        # Menú Opciones
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Cambiar fuente", command=self.select_font)
        options_menu.add_command(label="Cambiar velocidad máxima", command=self.change_max_speed)
    
    def select_font(self):
        fonts = list(font.families())
        current_font = self.config.get('font_family', 'Noto Mono')
        current_size = self.config.get('font_size', 10)
        
        font_dialog = tk.Toplevel(self.root)
        font_dialog.title("Seleccionar Fuente")
        
        # Lista de fuentes
        ttk.Label(font_dialog, text="Fuente:").grid(row=0, column=0, padx=5, pady=5)
        font_var = tk.StringVar(value=current_font)
        font_list = ttk.Combobox(font_dialog, textvariable=font_var, values=fonts)
        font_list.grid(row=0, column=1, padx=5, pady=5)
        
        # Tamaño de fuente
        ttk.Label(font_dialog, text="Tamaño:").grid(row=1, column=0, padx=5, pady=5)
        size_var = tk.IntVar(value=current_size)
        size_spin = ttk.Spinbox(font_dialog, from_=6, to=72, textvariable=size_var)
        size_spin.grid(row=1, column=1, padx=5, pady=5)
        
        def apply_font():
            self.config['font_family'] = font_var.get()
            self.config['font_size'] = size_var.get()
            self.text_widget.configure(font=(font_var.get(), size_var.get()))
            self.save_config()
            font_dialog.destroy()
        
        ttk.Button(font_dialog, text="Aplicar", command=apply_font).grid(row=2, column=0, columnspan=2, pady=10)
    
    def new_file(self):
        self.text_widget.delete('1.0', tk.END)
        self.current_file = None
        self.root.title("Lector y Editor de Texto - Nuevo archivo")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file_path:
            self.load_file(file_path)
    
    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert('1.0', content)
            self.current_file = file_path
            self.root.title(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            content = self.text_widget.get('1.0', tk.END)
            with open(self.current_file, 'w', encoding='utf-8') as file:
                file.write(content)
            messagebox.showinfo("Guardado", "Archivo guardado exitosamente.")
        else:
            self.save_file_as()
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if file_path:
            content = self.text_widget.get('1.0', tk.END)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            self.current_file = file_path
            self.root.title(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
            messagebox.showinfo("Guardado", "Archivo guardado exitosamente.")
    
    def start_scrolling(self):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_text()
    
    def pause_scrolling(self):
        self.is_scrolling = False
    
    def scroll_text(self):
        if self.is_scrolling:
            self.text_widget.yview_scroll(1, 'units')
            self.root.after(self.scroll_speed, self.scroll_text)
    
    def calculate_speed(self, value):
        min_speed = 1
        factor = math.log(self.max_speed / min_speed) / 29
        return max(1, int(min_speed * math.exp(factor * (30 - value))))
    
    def update_speed(self, *args):
        self.scroll_speed = self.calculate_speed(self.speed_var.get())
    
    def change_max_speed(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Cambiar velocidad máxima")
        dialog.geometry("300x100")
        
        ttk.Label(dialog, text="Nueva velocidad máxima (1-1000):").pack(pady=5)
        speed_var = tk.IntVar(value=self.max_speed)
        speed_entry = ttk.Spinbox(dialog, from_=1, to=1000, textvariable=speed_var)
        speed_entry.pack(pady=5)
        
        def apply_speed():
            new_speed = speed_var.get()
            if 1 <= new_speed <= 1000:
                self.max_speed = new_speed
                self.update_speed()
                self.save_config()
                messagebox.showinfo("Velocidad actualizada",
                                  f"La velocidad máxima se ha actualizado a {self.max_speed}.")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "La velocidad debe estar entre 1 y 1000")
        
        ttk.Button(dialog, text="Aplicar", command=apply_speed).pack(pady=5)
    
    def show_transpose_menu(self):
        menu = tk.Menu(self.root, tearoff=0)
        for i in range(-7, 8):
            menu.add_command(
                label=f"{i:+d}" if i != 0 else "0 (Original)",
                command=lambda x=i: self.transpose_chords(x))
        menu.post(self.transpose_button.winfo_rootx(),
                 self.transpose_button.winfo_rooty() + self.transpose_button.winfo_height())
    
    def transpose_chords(self, semitones):
        content = self.text_widget.get('1.0', tk.END)
        transposed_content = self.transpose_text(content, semitones)
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert('1.0', transposed_content)
    
    def transpose_text(self, text, semitones):
        chord_pattern = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)'
        
        chord_base = [
            ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'],
            ['F#', 'Gb'], ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
        ]
        
        def transpose_chord(chord, spaces_after):
            root = chord[0]
            accidental = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + accidental):]
            
            current_index = next(i for i, group in enumerate(chord_base) if root + accidental in group)
            new_index = (current_index + semitones) % len(chord_base)
            new_root = chord_base[new_index][0]
            
            if len(chord_base[new_index]) > 1:
                new_root = chord_base[new_index][0] if semitones > 0 else chord_base[new_index][1]
            
            new_chord = new_root + suffix
            
            if accidental and not ('#' in new_chord or 'b' in new_chord):
                spaces_after += 1
            elif not accidental and ('#' in new_chord or 'b' in new_chord):
                if spaces_after > 0:
                    spaces_after -= 0
            
            return new_chord, ' ' * spaces_after
        
        def process_line(line):
            chord_positions = list(re.finditer(chord_pattern, line))
            if not chord_positions:
                return line
            
            new_line = []
            last_end = 0
            
            for i, match in enumerate(chord_positions):
                new_line.append(line[last_end:match.start()])
                
                next_pos = chord_positions[i+1].start() if i+1 < len(chord_positions) else len(line)
                spaces_after = next_pos - match.end()
                
                new_chord, new_spaces = transpose_chord(match.group(), spaces_after)
                new_line.append(new_chord + new_spaces)
                
                last_end = next_pos
            
            new_line.append(line[last_end:])
            return ''.join(new_line)
        
        lines = text.split('\n')
        transposed_lines = [process_line(line) for line in lines]
        return '\n'.join(transposed_lines)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'max_speed': 100,
                'font_family': 'Noto Mono',
                'font_size': 10
            }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f)

def main():
    root = tk.Tk()
    app = TextScrollerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
