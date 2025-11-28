from pathlib import Path
import os
import shutil

import whisper


# ====== CONFIGURACIÓN FFMPEG LOCAL ======

BASE_DIR = Path(__file__).resolve().parent.parent
FFMPEG_DIR = BASE_DIR / "ffmpeg"


def setup_ffmpeg() -> None:
    # ffmpeg ya disponible globalmente
    if shutil.which("ffmpeg"):
        return

    # ffmpeg incluido en el proyecto 
    local_ffmpeg = FFMPEG_DIR / "ffmpeg.exe"
    if local_ffmpeg.exists():
        os.environ["PATH"] = str(FFMPEG_DIR) + os.pathsep + os.environ.get("PATH", "")
        return

    print(
        "[WARN] No se encontró ffmpeg en PATH ni en la carpeta 'ffmpeg/'. "
        "Asegúrate de incluir ffmpeg.exe en IA/ffmpeg o tener ffmpeg instalado en el sistema."
    )


setup_ffmpeg()


# ====== MODELO WHISPER LOCAL ======

# Carga del modelo local (tiny)
MODEL = whisper.load_model("tiny")


def transcribe_audio(audio_path: str, language: str = "es"):
    audio_path = Path(audio_path).resolve().as_posix()

    print(f"[INFO] Transcribiendo localmente: {audio_path}")

    result = MODEL.transcribe(
        audio_path,
        language=language,
        fp16=False 
    )

    return {
        "text": result.get("text", ""),
        "segments": result.get("segments", []),
        "language": language,
    }
