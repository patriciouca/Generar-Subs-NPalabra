import whisperx
import gc 
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import tkinter as tk
from tkinter import filedialog, messagebox
import os  # Necesario para borrar los archivos.
import time  # Necesario para obtener el timestamp.
import random


def select_video_file():
    file_path = filedialog.askopenfilename(title="Selecciona un archivo de video", filetypes=[("Video Files", "*.mp4;*.avi;*.mkv"), ("All Files", "*.*")])
    return file_path


def create_srt_content_random_words(data, minimo, maximo):
    """Genera el contenido del archivo .srt a partir de los datos proporcionados, 
       con un número aleatorio de palabras por subtítulo entre minimo y maximo."""
    
    srt_content = ""
    word_segments = data['word_segments']
    idx = 0
    subtitle_idx = 1

    while idx < len(word_segments):
        n = random.randint(minimo, maximo)  # Selecciona un número aleatorio de palabras para este subtítulo

        if 'start' in word_segments[idx]:
            start_time = seconds_to_srt_time(word_segments[idx]['start'])
        else:
            idx += 1
            continue

        # El tiempo final es el final del n-ésimo segmento o el final del último segmento si estamos en el final de word_segments
        if idx + n - 1 < len(word_segments) and 'end' in word_segments[idx + n - 1]:
            end_time = seconds_to_srt_time(word_segments[idx + n - 1]['end'])
            segment_text = ' '.join([word['word'] for word in word_segments[idx:idx + n]])
        elif 'end' in word_segments[-1]:
            end_time = seconds_to_srt_time(word_segments[-1]['end'])
            segment_text = ' '.join([word['word'] for word in word_segments[idx:]])
        else:
            idx += 1
            continue

        srt_content += f"{subtitle_idx}\n{start_time} --> {end_time}\n{segment_text}\n\n"

        idx += n
        subtitle_idx += 1

    return srt_content

def seconds_to_srt_time(seconds):
    """Convierte segundos a formato de tiempo hh:mm:ss,ms para .srt"""
    hours, remainder = divmod(seconds, 3600)
    minutes, remainder = divmod(remainder, 60)
    seconds, milliseconds = divmod(remainder, 1)
    return "{:02}:{:02}:{:02},{:03}".format(int(hours), int(minutes), int(seconds), int(milliseconds*1000))

def create_srt_content_n_words(data, n):
    """Genera el contenido del archivo .srt a partir de los datos proporcionados, con n palabras por subtítulo"""
    srt_content = ""
    word_segments = data['word_segments']
    idx = 0
    subtitle_idx = 1

    while idx < len(word_segments):
        if 'start' in word_segments[idx]:
            start_time = seconds_to_srt_time(word_segments[idx]['start'])
        else:
            continue  # Puedes decidir hacer algo diferente aquí

        # El tiempo final es el final del n-ésimo segmento o el final del último segmento si estamos en el final de word_segments
        if idx + n - 1 < len(word_segments) and 'end' in word_segments[idx + n - 1]:
            end_time = seconds_to_srt_time(word_segments[idx + n - 1]['end'])
            segment_text = ' '.join([word['word'] for word in word_segments[idx:idx + n]])
        elif 'end' in word_segments[-1]:
            end_time = seconds_to_srt_time(word_segments[-1]['end'])
            segment_text = ' '.join([word['word'] for word in word_segments[idx:]])
        else:
            continue  # De nuevo, puedes decidir hacer algo diferente aquía

        srt_content += f"{subtitle_idx}\n{start_time} --> {end_time}\n{segment_text}\n\n"

        idx += n
        subtitle_idx += 1

    return srt_content





def create_srt_content(data):
    """Genera el contenido del archivo .srt a partir de los datos proporcionados"""
    srt_content = ""
    for idx, segment in enumerate(data['segments']):
        start_time = seconds_to_srt_time(segment['start'])
        end_time = seconds_to_srt_time(segment['end'])
        srt_content += f"{idx + 1}\n{start_time} --> {end_time}\n{segment['text']}\n\n"
    return srt_content

def process_video():
    video_path = select_video_file()
    if not video_path:
        messagebox.showinfo("Información", "No se seleccionó ningún archivo.")
        return

    choice = choice_var.get()  # Obtiene la elección del usuario


    device = "cuda" 
    batch_size = 16 # reduce if low on GPU mem
    compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)


    video = VideoFileClip(video_path)

    # Extract audio
    audio = video.audio
    audio_path = "audio.wav"
    audio.write_audiofile(audio_path)

    # Load .wav audio file
    audio_wav = AudioSegment.from_wav(audio_path)

    # Convert to .mp3
    mp3_path = "audio.mp3"
    audio_wav.export(mp3_path, format="mp3")


    #model = whisper.load_model("medium")
    #result = model.transcribe("audio.mp3")
    #print(result)

    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model("large-v2", device, compute_type=compute_type)
    audio = whisperx.load_audio(mp3_path)
    result = model.transcribe(audio, batch_size=batch_size)
    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)


    if not os.path.exists("subtitulos"):
        os.makedirs("subtitulos")

     # Usar un timestamp para el nombre del archivo.

    if choice == "fixed":
        n = n_words_entry.get()
        try:
            n = int(n)
            srt_content = create_srt_content_n_words(result, n)
        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce un número válido de palabras.")
            return

    elif choice == "random":
        try:
            minimo = int(min_words_entry.get())
            maximo = int(max_words_entry.get())
            
            if minimo > maximo:
                messagebox.showerror("Error", "El número mínimo de palabras no puede ser mayor que el máximo.")
                return

            srt_content = create_srt_content_random_words(result, minimo, maximo)

        except ValueError:
            messagebox.showerror("Error", "Por favor, introduce números válidos para las palabras mínimas y máximas.")
            return
        
    print(result)

    timestamp = int(time.time())
    file_path = os.path.join("subtitulos", f"subtitulos_{timestamp}.srt")

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(srt_content)

    os.remove("audio.wav")
    os.remove("audio.mp3")
    
    messagebox.showinfo("Información", "Proceso completado. Se generaron los subtítulos.")


def update_interface():
    """Muestra u oculta campos de la interfaz según la elección del usuario."""
    choice = choice_var.get()
    
    # Desempaquetamos todos los widgets primero
    btn_process.pack_forget()
    n_words_label.pack_forget()
    n_words_entry.pack_forget()
    min_words_label.pack_forget()
    min_words_entry.pack_forget()
    max_words_label.pack_forget()
    max_words_entry.pack_forget()

    if choice == "fixed":
        # Mostrar campo para número fijo, ocultar campos para números aleatorios
        n_words_label.pack(pady=(5,5))
        n_words_entry.pack(pady=(0,5))
    elif choice == "random":
        # Ocultar campo para número fijo, mostrar campos para números aleatorios
        min_words_label.pack(pady=(5,5))
        min_words_entry.pack(pady=(0,5))
        max_words_label.pack(pady=(5,5))
        max_words_entry.pack(pady=(0,20))

    # Empacamos btn_process al final, sin importar la opción
    btn_process.pack(pady=10)





def launch_gui():
    root = tk.Tk()
    root.title("Generador de Subtítulos")
    
    # Establecer tamaño predeterminado, por ejemplo 400x200.
    root.geometry("500x300")
    
    # Centrar la ventana
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # Calcula x e y para que la ventana aparezca centrada
    x = (screen_width / 2) - (400 / 2)
    y = (screen_height / 2) - (200 / 2)
    
    root.geometry(f"+{int(x)}+{int(y)}")

    frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(padx=10, pady=10)

    global choice_var, n_words_entry, min_words_entry, max_words_entry,n_words_label, max_words_label,min_words_label
    choice_var = tk.StringVar(value="fixed")  # Esto es para manejar si el usuario quiere usar n fijo o rango aleatorio
    
    # Radiobuttons para decidir el método
    rad_fixed = tk.Radiobutton(frame, text="Usar número fijo de palabras", variable=choice_var, value="fixed")
    rad_fixed.pack(pady=(10,5))
    
    rad_random = tk.Radiobutton(frame, text="Usar número aleatorio de palabras", variable=choice_var, value="random")
    rad_random.pack(pady=(5,5))
    
    # Entrada para el número fijo n
    n_words_label = tk.Label(frame, text="Número de palabras por subtítulo:")
    n_words_label.pack(pady=(5,5))
    n_words_entry = tk.Entry(frame)
    n_words_entry.pack(pady=(0,5))
    
    # Entrada para el número mínimo de palabras
    min_words_label = tk.Label(frame, text="Número mínimo de palabras:")
    min_words_label.pack(pady=(5,5))
    min_words_entry = tk.Entry(frame)
    min_words_entry.pack(pady=(0,5))
    
    # Entrada para el número máximo de palabras
    max_words_label = tk.Label(frame, text="Número máximo de palabras:")
    max_words_label.pack(pady=(5,5))
    max_words_entry = tk.Entry(frame)
    max_words_entry.pack(pady=(0,20))

    # Vincula la función update_interface a los Radiobuttons
    rad_fixed.config(command=update_interface)
    rad_random.config(command=update_interface)


    global btn_process
    btn_process = tk.Button(frame, text="Generar Subtítulos", command=process_video)
    update_interface()
    

    root.mainloop()




if __name__ == "__main__":
    launch_gui()
    btn_process.pack(pady=10)