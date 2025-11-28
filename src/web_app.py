from pathlib import Path
from datetime import datetime, timezone
import json
from typing import List, Dict, Any

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)

from .asr_service import transcribe_audio
from .transcript_repository import save_transcript, get_transcript_text

# =====================================================
#   EMBEDDINGS - LAZY LOAD
# =====================================================

SEMANTIC_MODEL = None  # aún no cargado


def load_semantic_model():
    global SEMANTIC_MODEL
    if SEMANTIC_MODEL is not None:
        return SEMANTIC_MODEL

    try:
        print("[INFO] Cargando modelo de embeddings (lazy-load)...")
        from sentence_transformers import SentenceTransformer  # type: ignore

        SEMANTIC_MODEL = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("[INFO] Modelo de embeddings cargado correctamente.")
        return SEMANTIC_MODEL
    except Exception as e:
        print(f"[WARN] No se pudo cargar el modelo de embeddings: {e}")
        SEMANTIC_MODEL = None
        return None


# =====================================================
#   PATHS Y CONFIG
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "data" / "audio"
TRANSCRIPTS_DIR = BASE_DIR / "data" / "transcripts"

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
app.secret_key = "marketing"


# =====================================================
#   HELPERS
# =====================================================

def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def load_transcript_json(filename: str) -> Dict[str, Any]:
    path = TRANSCRIPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de transcripción: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def keyword_search_segments(transcript_data: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    query_lower = query.lower().strip()
    segments = transcript_data.get("segments", [])
    results: List[Dict[str, Any]] = []

    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        if query_lower in text.lower():
            results.append(
                {
                    "text": text,
                    "start": seg.get("start"),
                    "end": seg.get("end"),
                    "score": 1.0,
                }
            )

    # Fallback si no hay segments
    if not segments and query_lower in (transcript_data.get("text", "") or "").lower():
        results.append(
            {
                "text": transcript_data.get("text", ""),
                "start": None,
                "end": None,
                "score": 1.0,
            }
        )

    return results


def semantic_search_segments(transcript_data: Dict[str, Any], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    model = load_semantic_model()
    if model is None:
        # No hay modelo disponible
        return []

    from sentence_transformers import util  # import aquí para no hacerlo al inicio

    segments = transcript_data.get("segments", [])
    texts = [(seg.get("text") or "").strip() for seg in segments]
    indexed = [(i, t) for i, t in enumerate(texts) if t]

    if not indexed:
        # Fallback: texto completo
        full_text = (transcript_data.get("text") or "").strip()
        if not full_text:
            return []
        query_emb = model.encode(query, convert_to_tensor=True)
        text_emb = model.encode(full_text, convert_to_tensor=True)
        score = float(util.cos_sim(query_emb, text_emb)[0][0])
        return [
            {
                "text": full_text,
                "start": None,
                "end": None,
                "score": score,
            }
        ]

    idxs, clean_texts = zip(*indexed)

    query_emb = model.encode(query, convert_to_tensor=True)
    seg_embs = model.encode(list(clean_texts), convert_to_tensor=True)
    cos_scores = util.cos_sim(query_emb, seg_embs)[0]

    top_k = min(top_k, len(clean_texts))
    top_results = cos_scores.topk(k=top_k)

    results: List[Dict[str, Any]] = []
    for score, idx_pos in zip(top_results.values, top_results.indices):
        idx = idxs[int(idx_pos)]
        seg = segments[idx]
        results.append(
            {
                "text": (seg.get("text") or "").strip(),
                "start": seg.get("start"),
                "end": seg.get("end"),
                "score": float(score),
            }
        )

    return results


# =====================================================
#   RUTAS
# =====================================================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("audio_file")
        language = request.form.get("language", "es")

        if not file or file.filename == "":
            flash("Por favor selecciona un archivo de audio.", "error")
            return redirect(url_for("index"))

        if not allowed_file(file.filename):
            flash("Formato de archivo no permitido. Usa mp3, wav, m4a, ogg o flac.", "error")
            return redirect(url_for("index"))

        # Crear carpetas si no existen
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

        # Nombre único
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        original_name = Path(file.filename).stem
        safe_name = f"{original_name}_{timestamp}"
        audio_path = UPLOAD_DIR / f"{safe_name}{Path(file.filename).suffix}"

        file.save(str(audio_path))

        # Transcribir
        try:
            transcript_data = transcribe_audio(
                str(audio_path),
                language=language,
            )
        except Exception as e:
            print(f"[ERROR] Falló la transcripción: {e}")
            flash("Ocurrió un error al transcribir el audio.", "error")
            return redirect(url_for("index"))

        # Guardar JSON de transcripción
        transcript_path = TRANSCRIPTS_DIR / f"{safe_name}.json"
        save_transcript(transcript_data, str(transcript_path))

        # Texto para mostrar
        text = get_transcript_text(transcript_data)

        return render_template(
            "result.html",
            transcript_text=text,
            transcript_file=transcript_path.name,
            language=language,
            query=None,
            mode="keyword",
            results=[],
            semantic_enabled=True,
        )

    return render_template("index.html")


@app.route("/search/<filename>", methods=["POST"])
def search_in_transcript(filename: str):
    query = request.form.get("query", "").strip()
    mode = request.form.get("mode", "keyword")

    if not query:
        flash("Ingresa una palabra o frase para buscar.", "error")
        return redirect(url_for("view_transcript_file_human", filename=filename))

    try:
        transcript_data = load_transcript_json(filename)
    except FileNotFoundError:
        flash("No se encontró la transcripción seleccionada.", "error")
        return redirect(url_for("index"))

    full_text = transcript_data.get("text") or ""
    results: List[Dict[str, Any]] = []

    if mode == "semantic":
        # intentamos semántica; si no se puede, fallback a keyword
        results = semantic_search_segments(transcript_data, query, top_k=5)
        if not results:
            flash("La búsqueda semántica no está disponible en este entorno. Se usará búsqueda por palabra clave.", "error")
            mode = "keyword"

    if mode == "keyword":
        results = keyword_search_segments(transcript_data, query)

    if not results:
        flash("No se encontraron coincidencias para esa consulta.", "info")

    language = transcript_data.get("language", "es")

    return render_template(
        "result.html",
        transcript_text=full_text,
        transcript_file=filename,
        language=language,
        query=query,
        mode=mode,
        results=results,
        semantic_enabled=True,
    )


@app.route("/transcript/<filename>")
def view_transcript_file(filename: str):
    path = TRANSCRIPTS_DIR / filename
    if not path.exists():
        flash("No se encontró el archivo de transcripción.", "error")
        return redirect(url_for("index"))

    content = path.read_text(encoding="utf-8")
    return app.response_class(
        response=content,
        status=200,
        mimetype="application/json",
    )


@app.route("/transcript_view/<filename>")
def view_transcript_file_human(filename: str):
    try:
        transcript_data = load_transcript_json(filename)
    except FileNotFoundError:
        flash("No se encontró la transcripción seleccionada.", "error")
        return redirect(url_for("index"))

    full_text = transcript_data.get("text") or ""
    language = transcript_data.get("language", "es")

    return render_template(
        "result.html",
        transcript_text=full_text,
        transcript_file=filename,
        language=language,
        query=None,
        mode="keyword",
        results=[],
        semantic_enabled=True,
    )


if __name__ == "__main__":
    app.run(debug=True)
