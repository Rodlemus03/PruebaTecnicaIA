import json
from pathlib import Path
from typing import Any, Dict


def save_transcript(transcript: Dict[str, Any], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=2)


def load_transcript(path: str) -> Dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de transcripción: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_transcript_text(transcript: Dict[str, Any]) -> str:
    text = transcript.get("text")
    if isinstance(text, str) and text.strip():
        return text

    # Fallback: concatenar segmentos si no hubiera 'text'
    segments = transcript.get("segments") or []
    if segments:
        joined = " ".join(seg.get("text", "") for seg in segments)
        return joined.strip()

    return ""
