from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    searxng_url: str = "http://localhost:8080"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:32b"
    max_results: int = 8
    timeout_seconds: int = 20
    max_source_blocks: int = 3
    max_chars_per_source: int = 2500
    ollama_num_predict: int = 900


def load_settings() -> Settings:
    load_dotenv_file(Path(".env"))
    return Settings(
        searxng_url=os.getenv("SEARXNG_URL", "http://localhost:8080").rstrip("/"),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/"),
        ollama_model=os.getenv("OLLAMA_MODEL", "qwen3:32b"),
        max_results=int(os.getenv("OPENCLAW_MAX_RESULTS", "8")),
        timeout_seconds=int(os.getenv("OPENCLAW_TIMEOUT_SECONDS", "20")),
        max_source_blocks=int(os.getenv("OPENCLAW_MAX_SOURCE_BLOCKS", "3")),
        max_chars_per_source=int(os.getenv("OPENCLAW_MAX_CHARS_PER_SOURCE", "2500")),
        ollama_num_predict=int(os.getenv("OPENCLAW_OLLAMA_NUM_PREDICT", "900")),
    )


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)
