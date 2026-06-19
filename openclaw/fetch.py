from __future__ import annotations

from dataclasses import dataclass

import requests
import trafilatura
from bs4 import BeautifulSoup


@dataclass(frozen=True)
class FetchedSource:
    url: str
    title: str
    text: str


def fetch_text(url: str, timeout: int) -> FetchedSource:
    response = requests.get(
        url,
        headers={"User-Agent": "OpenClawResearchLayer/0.1 local"},
        timeout=timeout,
    )
    response.raise_for_status()
    html = response.text
    extracted = trafilatura.extract(html, include_comments=False, include_tables=True)
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    return FetchedSource(url=url, title=title, text=(extracted or "").strip())

