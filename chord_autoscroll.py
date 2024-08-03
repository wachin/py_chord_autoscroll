import tkinter as tk
from tkinter import filedialog, messagebox
import math

class TextScrollerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Lector y Editor de Texto")
        self.master.geometry("700x400")

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

        self.is_scrolling = False
        self.scroll_speed = self.calculate_speed(15)  # Velocidad por defecto

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_widget.delete('1.0', tk.END)
                self.text_widget.insert(tk.END, content)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivos de texto", "*.txt")])
        if file_path:
            content = self.text_widget.get('1.0', tk.END)
            with open(file_path, 'w') as file:
                file.write(content)
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
            self.master.after(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        # Función exponencial para un cambio más progresivo
        min_speed = 320
        max_speed = 6400
        factor = math.log(max_speed / min_speed) / 29  # 29 es el rango (30 - 1)
        return int(min_speed * math.exp(factor * (30 - value)))

    def update_speed(self, value):
        self.scroll_speed = self.calculate_speed(float(value))

if __name__ == "__main__":
    root = tk.Tk()
    app = TextScrollerApp(root)
    root.mainloop()
