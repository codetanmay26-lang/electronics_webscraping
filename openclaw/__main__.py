from __future__ import annotations

import argparse
import json

from openclaw.config import load_settings
from openclaw.gap_detector import detect_gaps
from openclaw.gap_schema import entry_001_gap_assessment
from openclaw.pipeline import run_research


def run_doctor() -> dict[str, object]:
    settings = load_settings()
    report: dict[str, object] = {
        "settings": {
            "searxng_url": settings.searxng_url,
            "ollama_url": settings.ollama_url,
            "ollama_model": settings.ollama_model,
            "max_results": settings.max_results,
            "timeout_seconds": settings.timeout_seconds,
            "max_source_blocks": settings.max_source_blocks,
            "max_chars_per_source": settings.max_chars_per_source,
            "ollama_num_predict": settings.ollama_num_predict,
        },
        "ollama": {},
    }
    try:
        import requests

        response = requests.get(f"{settings.ollama_url}/api/tags", timeout=5)
        report["ollama"] = {
            "status_code": response.status_code,
            "body_preview": response.text[:500],
        }
    except Exception as exc:
        report["ollama"] = {"error": str(exc)}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenClaw local research layer")
    parser.add_argument("query", nargs="?", help="Research query to gather and structure")
    parser.add_argument(
        "--entry-001-gaps",
        action="store_true",
        help="Print the Entry 001 gap assessment JSON.",
    )
    parser.add_argument(
        "--detect-gaps",
        action="store_true",
        help="Run general prompt-level gap detection instead of web research.",
    )
    parser.add_argument(
        "--doctor",
        action="store_true",
        help="Print local OpenClaw settings and service health.",
    )
    args = parser.parse_args()

    if args.doctor:
        print(json.dumps(run_doctor(), indent=2, ensure_ascii=True))
        return

    if args.entry_001_gaps:
        print(entry_001_gap_assessment().model_dump_json(indent=2))
        return

    if not args.query:
        parser.error("query is required unless --entry-001-gaps is used")

    if args.detect_gaps:
        print(detect_gaps(args.query).model_dump_json(indent=2))
        return

    output = run_research(args.query, load_settings())
    print(output.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
