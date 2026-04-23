"""
config.py
─────────────────────────────────────────────────────────────────
Central configuration loader.
Reads ALL settings from .env via python-dotenv.

Usage anywhere in the project:
    from config import GROQ_API_KEY, GROQ_MODEL, ...

The API key is NEVER entered in the UI — it lives only in .env.
─────────────────────────────────────────────────────────────────
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root (works regardless of CWD) ────────
_PROJECT_ROOT = Path(__file__).parent
_ENV_PATH     = _PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=_ENV_PATH, override=False)   # won't override already-set env vars


# ── Internal helper ───────────────────────────────────────────────
def _require(key: str) -> str:
    """Raise a helpful error if a required env var is missing or still a placeholder."""
    val = os.getenv(key, "").strip()
    if not val or val.startswith("gsk_your"):
        raise EnvironmentError(
            f"\n\n❌  '{key}' is missing or still set to the placeholder value.\n"
            f"    Steps to fix:\n"
            f"      1. Copy .env.example  →  .env\n"
            f"      2. Open .env and replace the placeholder with your real key.\n"
            f"      3. Get a free Groq key at https://console.groq.com\n"
        )
    return val


# ── Groq (LLM) ───────────────────────────────────────────────────
GROQ_API_KEY: str = _require("GROQ_API_KEY")
GROQ_MODEL:   str = os.getenv("GROQ_MODEL", "qwen/qwen3-32b")

# ── Embeddings (runs locally, no API key needed) ──────────────────
EMBEDDING_MODEL: str = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2",
)

# ── Retriever ─────────────────────────────────────────────────────
RETRIEVER_TOP_K: int = int(os.getenv("RETRIEVER_TOP_K", "5"))

# ── Dataset ───────────────────────────────────────────────────────
DATA_PATH: Path = _PROJECT_ROOT / os.getenv("DATA_PATH", "data/tn_colleges.json")
