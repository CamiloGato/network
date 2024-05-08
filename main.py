import tkinter as tk
from tkinter import filedialog


def open_audio_file_dialog():
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter

    file_path = filedialog.askopenfilename(
        title="Seleccionar archivo de audio",
        filetypes=(("Archivos de audio", "*.wav;*.mp3"), ("Todos los archivos", "*.*"))
    )

    if file_path:
        print("Archivo de audio seleccionado:", file_path)
        # Aquí puedes realizar cualquier operación con el archivo de audio seleccionado


if __name__ == "__main__":
    open_audio_file_dialog()
