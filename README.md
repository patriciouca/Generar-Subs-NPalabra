# Generador de Subtítulos

Este proyecto es una herramienta que permite al usuario seleccionar un archivo de video y generar automáticamente subtítulos para él. La aplicación presenta una interfaz gráfica sencilla en la que el usuario puede especificar el número de palabras por subtítulo. Después de procesar el video, se genera un archivo `.srt` con los subtítulos correspondientes.

## Características

- Interfaz gráfica sencilla para la selección de videos y especificación de configuraciones.
- Utiliza el modelo `whisperx` para la transcripción y alineación del audio del video.
- Permite al usuario definir el número de palabras por subtítulo.
- Genera archivos `.srt` con nombres basados en timestamp para evitar conflictos.
- Guarda los archivos `.srt` en una carpeta dedicada para una organización sencilla.

## Requisitos

El proyecto depende de varias bibliotecas externas. A continuación, se enumeran las principales dependencias:

- `whisperx`: Utilizada para la transcripción y alineación del audio.
- `tkinter`: Biblioteca de interfaz gráfica para Python.
- `pydub`: Para manipulación de archivos de audio.
- `moviepy`: Para extraer audio de videos.

  ```bash
   pip install whisperx tkinter pydub moviepy
   python [nombre_del_script].py

## Instalación

1. Clone este repositorio:

   ```bash
   git clone https://github.com/patriciouca/Generar-Subs-NPalabra
   cd Generar-Subs-NPalabra
