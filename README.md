# Transcripción de Audio con Búsqueda por Palabra Clave y Búsqueda Semántica (Prueba Técnica)

Este proyecto implementa un sistema completo de transcripción de audio en español utilizando modelos de reconocimiento automático de voz (ASR), junto con funcionalidades de búsqueda literal y búsqueda semántica dentro de la transcripción.

El objetivo principal es cumplir con los requisitos de la prueba técnica, demostrando integración con un servicio de transcripción, almacenamiento estructurado del resultado y mecanismos de consulta sobre el contenido transcrito. Además, se incluye una opción de búsqueda semántica basada en embeddings como valor adicional.

---

## Características principales

1. Transcripción de audio local mediante el modelo Whisper.
2. Procesamiento y almacenamiento del resultado en formato JSON.
3. Interfaz web en Flask para:
   - Subir un archivo de audio.
   - Visualizar la transcripción generada.
   - Realizar búsquedas por palabra clave.
   - Realizar búsquedas semánticas (opcional).
4. Búsqueda literal por coincidencia exacta de texto.
5. Búsqueda semántica con embeddings mediante SentenceTransformer (lazy-load para mejorar tiempo de carga).
6. Ejecución autónoma sin dependencias externas, gracias a la inclusión de FFmpeg local dentro del proyecto.
7. Script CLI para transcribir audio desde la terminal.

---

## Video de demostración

Demostración completa del funcionamiento del sistema:  
https://youtu.be/iZnoL5oYTc0

---

## Repositorio del proyecto

[https://github.com/Rodlemus03/PruebaTecnicaIA]
---

## Arquitectura del proyecto
project/
│
├── data/
│ ├── audio/ # Archivos de audio de entrada
│ └── transcripts/ # Transcripciones generadas en JSON
│
├── ffmpeg/ # FFmpeg local para funcionamiento autónomo
│ ├── ffmpeg.exe
│ ├── ffplay.exe
│ └── ffprobe.exe
│
├── src/
│ ├── init.py
│ ├── asr_service.py # Lógica de transcripción Whisper + FFmpeg
│ ├── transcribe_audio.py # Script CLI
│ ├── transcript_repository.py
│ └── web_app.py # Servidor Flask + búsquedas
│
├── static/
│ └── styles.css # Estilos de la interfaz web
│
├── templates/
│ ├── index.html
│ ├── layout.html
│ └── result.html
│
├── README.md
└── requirements.txt

## Instalación

1. Clonar el repositorio.

2. Instalar dependencias: pip install -r requirements.txt

3.  No se requiere instalación de FFmpeg en el sistema.  
   FFmpeg está incluido en el proyecto y es utilizado desde el directorio local.

## Uso

### Ejecutar la aplicación web

Luego acceder en el navegador:

http://127.0.0.1:5000


La aplicación permite:

- Subir un archivo de audio.
- Transcribirlo localmente.
- Visualizar la transcripción.
- Buscar texto dentro de la transcripción.
- Realizar búsqueda semántica si el modelo de embeddings puede cargarse en el entorno.

La carga del modelo de embeddings utiliza un sistema de lazy-load para evitar demoras durante el inicio del servidor.

---

### Ejecutar la transcripción desde la terminal
python -m src.transcribe_audio data/audio/audio_entrada.mp3


Esto generará un archivo JSON en `data/transcripts/`.

---

## Búsquedas

### Búsqueda por palabra clave

Realiza coincidencias literales (insensitive case) sobre los segmentos transcritos.

### Búsqueda semántica

Usa embeddings generados por SentenceTransformer (`all-MiniLM-L6-v2`).  
Permite encontrar fragmentos relacionados aunque las palabras no coincidan literalmente.

Esta función es opcional y se activa solo si el entorno soporta el modelo.

---

## Servicio y modelo de ASR utilizados

El sistema utiliza el modelo Whisper en su variante local, ejecutado mediante la librería `openai-whisper`. Whisper es un modelo de reconocimiento automático de voz desarrollado por OpenAI y disponible para uso local sin necesidad de llamadas a una API externa.

Whisper permite realizar transcripciones en español con una precisión adecuada para audios cortos y de buena calidad, cumpliendo correctamente los requerimientos de esta prueba técnica.

### Limitaciones conocidas

- El desempeño puede verse afectado por ruido de fondo, ecos o grabaciones de baja calidad.
- Los modelos pequeños de Whisper (como `tiny`) priorizan velocidad sobre precisión, lo que puede generar errores en frases complejas.
- Audios largos requieren más tiempo de procesamiento.
- No incluye funcionalidades adicionales como diarización (identificación de hablantes) o traducción en esta implementación.
- La ejecución es local y depende directamente de los recursos disponibles en el equipo.

---

## Notas técnicas

- FFmpeg se resuelve mediante rutas locales para evitar configuraciones adicionales en el PATH del sistema.
- Whisper se ejecuta localmente y no depende de servicios externos.
- El sistema utiliza carga diferida del modelo de embeddings para optimizar el tiempo de inicio.
- La aplicación está diseñada para ejecutarse únicamente con `pip install -r requirements.txt`, sin configuraciones adicionales.

---

## Requerimientos mínimos

- Python 3.10 o superior  
- Pip actualizado  
- 2 GB de RAM (mínimo recomendado)  
- Sistema operativo Windows, macOS o Linux  

---

## Contacto

Para consultas técnicas sobre esta prueba o su implementación:

Correo: rodlemus03@gmail.com  
Teléfono: 30426422  

Mauricio Lemus
