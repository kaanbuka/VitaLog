"""Optional server-side speech-to-text (only used by /voice).

The default VitaLog flow performs STT in the user's browser (Web Speech API,
free, no key) and POSTs the recognized text to /text — so this module is
**not required** for normal operation.

If you want to also accept raw audio uploads at /voice, two free/paid options
are supported, in order of preference:

1. **OpenAI Whisper API** — set ``OPENAI_API_KEY`` in ``.env`` (paid, accurate).
2. **faster-whisper (local, free, offline)** — install with::

       pip install faster-whisper

   Set ``LOCAL_WHISPER_MODEL`` (default ``small``). First run downloads the
   model (~150 MB for ``small``, ~75 MB for ``base``).

If neither is available we fall back to the original upload filename — just
enough to keep the pipeline testable without any STT setup.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.getenv("OPENAI_API_KEY")
_OPENAI_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
_LOCAL_MODEL = os.getenv("LOCAL_WHISPER_MODEL", "small")


@lru_cache(maxsize=1)
def _local_whisper():
    """Lazy-load faster-whisper. Returns None if not installed."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    return WhisperModel(_LOCAL_MODEL, device="cpu", compute_type="int8")


def _via_openai(path: Path) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=_API_KEY)
    with path.open("rb") as f:
        result = client.audio.transcriptions.create(
            model=_OPENAI_MODEL, file=f, language="tr", response_format="text"
        )
    return str(result).strip()


def _via_local(path: Path) -> str:
    model = _local_whisper()
    assert model is not None
    segments, _ = model.transcribe(str(path), language="tr", vad_filter=True)
    return " ".join(s.text.strip() for s in segments).strip()


def transcribe_audio(path: Path, *, hint_filename: str | None = None) -> str:
    """Transcribe a Turkish audio recording. Picks the best available backend."""
    if _API_KEY:
        return _via_openai(path)
    if _local_whisper() is not None:
        return _via_local(path)
    # Last-resort dev fallback: derive transcript from upload filename.
    stem = Path(hint_filename or path.name).stem
    return stem.replace("_", " ").replace("-", " ")
