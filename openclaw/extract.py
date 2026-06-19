from __future__ import annotations

import json

import requests

from openclaw.schema import ResearchOutput


SYSTEM_PROMPT = """You are OpenClaw, a local research and grounding subsystem.

You only extract, verify, cite, and structure technical information from supplied sources.
You must not design circuits, choose final components, simulate, optimize, infer missing
values, or make engineering conclusions.

Return only valid JSON matching the requested schema. If a value is not present in the
sources, write "not found" or add a limitation. Every important fact must be traceable to
a source URL supplied in the context.
"""


def extract_with_ollama(
    ollama_url: str,
    model: str,
    query: str,
    source_blocks: list[str],
    timeout: int,
    num_predict: int,
) -> ResearchOutput:
    schema_hint = ResearchOutput(query=query).model_dump()
    prompt = {
        "query": query,
        "required_json_shape": schema_hint,
        "sources": source_blocks,
    }
    response = requests.post(
        f"{ollama_url}/api/generate",
        json={
            "model": model,
            "system": SYSTEM_PROMPT,
            "prompt": json.dumps(prompt, ensure_ascii=True),
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
                "num_predict": num_predict,
            },
        },
        timeout=timeout,
    )
    if response.status_code >= 400:
        raise RuntimeError(
            f"Ollama returned HTTP {response.status_code}: {response.text[:500]}"
        )
    raw = response.json().get("response", "{}")
    return ResearchOutput.model_validate_json(raw)


def fallback_extract(query: str, source_urls: list[str], limitation: str) -> ResearchOutput:
    return ResearchOutput(
        query=query,
        summary="Local extraction model unavailable; returning gathered source URLs only.",
        source_urls=source_urls,
        limitations_or_missing_data=[limitation],
    )
