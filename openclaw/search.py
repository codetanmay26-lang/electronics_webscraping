from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import requests


OFFICIAL_DOMAINS = (
    "ti.com",
    "analog.com",
    "st.com",
    "infineon.com",
    "microchip.com",
    "onsemi.com",
    "nxp.com",
    "renesas.com",
    "vishay.com",
    "mouser.com",
    "digikey.com",
)


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    score: float


def search_searxng(base_url: str, query: str, max_results: int, timeout: int) -> list[SearchResult]:
    response = requests.get(
        f"{base_url}/search",
        params={"q": query, "format": "json", "language": "en"},
        headers={"User-Agent": "OpenClawResearchLayer/0.1 local"},
        timeout=timeout,
    )
    response.raise_for_status()
    payload = response.json()
    results = []
    for item in payload.get("results", [])[:max_results]:
        url = item.get("url", "")
        results.append(
            SearchResult(
                title=item.get("title", ""),
                url=url,
                snippet=item.get("content", ""),
                score=rank_url(url),
            )
        )
    return sorted(results, key=lambda result: result.score, reverse=True)


def rank_url(url: str) -> float:
    host = urlparse(url).netloc.lower()
    score = 1.0
    if any(host.endswith(domain) for domain in OFFICIAL_DOMAINS):
        score += 3.0
    if "datasheet" in url.lower():
        score += 1.0
    if "application-note" in url.lower() or "appnote" in url.lower():
        score += 1.0
    if url.lower().endswith(".pdf"):
        score += 0.5
    return score
