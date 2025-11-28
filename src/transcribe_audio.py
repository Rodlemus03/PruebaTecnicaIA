import argparse
from pathlib import Path

from .asr_service import transcribe_audio
from .transcript_repository import save_transcript


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe un archivo de audio usando Whisper local y guarda el resultado en JSON."
    )
    parser.add_argument(
        "audio_path",
        type=str,
        help="Ruta al archivo de audio (mp3, wav, m4a, etc.).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help=(
            "Ruta de salida para el JSON de la transcripción. "
            "Por defecto: data/transcripts/<nombre_archivo>.json"
        ),
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        default="es",
        help="Idioma del audio (por defecto 'es').",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    audio_path = Path(args.audio_path)
    if not audio_path.exists():
        raise SystemExit(f"[ERROR] No se encontró el archivo de audio: {audio_path}")

    # Nos aseguramos de trabajar con una ruta absoluta
    audio_path_resolved = audio_path.resolve()

    if args.output:
        output_path = Path(args.output)
    else:
        output_dir = Path("data") / "transcripts"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / (audio_path_resolved.stem + ".json")

    print(f"[INFO] Transcribiendo audio: {audio_path_resolved}")
    transcript = transcribe_audio(str(audio_path_resolved), language=args.language)

    save_transcript(transcript, str(output_path))
    print(f"[OK] Transcripción guardada en: {output_path}")


if __name__ == "__main__":
    main()
