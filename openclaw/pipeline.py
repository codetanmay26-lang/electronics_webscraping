from __future__ import annotations

from openclaw.config import Settings
from openclaw.gap_detector import detect_gaps
from openclaw.guardrails import guardrail_message, is_prohibited_request
from openclaw.schema import ResearchOutput, empty_research_output


def run_research(query: str, settings: Settings) -> ResearchOutput:
    if is_prohibited_request(query):
        gap_result = detect_gaps(query)
        return ResearchOutput(
            query=query,
            summary=(
                "OpenClaw detected a design-style request and did not perform engineering design. "
                "It identified the research requirements and gaps that should be gathered before "
                "a downstream Electronics AI attempts design work."
            ),
            key_concepts=[
                requirement.requirement for requirement in gap_result.detected_requirements
            ],
            engineering_constraints=[
                requirement.evidence
                for requirement in gap_result.detected_requirements
                if requirement.category == "explicit_specification"
            ],
            key_specifications=[
                f"{item.category}: {item.description} Priority: {item.priority}"
                for item in gap_result.missing_information
            ],
            limitations_or_missing_data=[
                guardrail_message(),
                *[
                    f"Research needed: {task}"
                    for task in gap_result.research_tasks_needed
                ],
                *[
                    f"Blocked downstream step: {step}"
                    for step in gap_result.blocked_downstream_steps
                ],
                *gap_result.limitations,
            ],
        )

    try:
        from openclaw.search import search_searxng

        results = search_searxng(
            settings.searxng_url,
            query,
            settings.max_results,
            settings.timeout_seconds,
        )
    except Exception as exc:
        return empty_research_output(query, f"SearXNG search failed: {exc}")

    fetched_blocks: list[str] = []
    source_urls: list[str] = []
    for result in results:
        source_urls.append(result.url)
        if _is_low_quality_url(result.url):
            continue
        if len(fetched_blocks) >= settings.max_source_blocks:
            continue
        source_text = ""
        source_title = result.title
        try:
            from openclaw.fetch import fetch_text

            source = fetch_text(result.url, settings.timeout_seconds)
            source_text = source.text
            source_title = source.title or result.title
        except Exception:
            source_text = ""

        if not source_text:
            source_text = result.snippet
        if not source_text:
            continue

        fetched_blocks.append(
            "\n".join(
                [
                    f"URL: {result.url}",
                    f"TITLE: {source_title}",
                    "TEXT:",
                    source_text[: settings.max_chars_per_source],
                ]
            )
        )

    if not fetched_blocks:
        return url_only_research_output(
            query,
            source_urls,
            "No readable source text found from searched URLs; returning URL-level research packet.",
        )

    try:
        from openclaw.extract import extract_with_ollama

        output = extract_with_ollama(
            settings.ollama_url,
            settings.ollama_model,
            query,
            fetched_blocks,
            settings.timeout_seconds,
            settings.ollama_num_predict,
        )
    except Exception as exc:
        return url_only_research_output(query, source_urls, f"Ollama extraction failed: {exc}")

    output.query = query
    output.source_urls = sorted(set(output.source_urls + source_urls))
    return output


def url_only_research_output(query: str, source_urls: list[str], limitation: str) -> ResearchOutput:
    output = ResearchOutput(
        query=query,
        summary=(
            "Web search completed and source URLs were gathered. Local model extraction "
            "did not complete, so this is a URL-level research packet."
        ),
        source_urls=source_urls,
        limitations_or_missing_data=[limitation],
    )
    for url in source_urls:
        lowered = url.lower()
        if "/lit/an/" in lowered or "application-note" in lowered or "app-note" in lowered:
            output.application_notes.append(
                {
                    "title": "Application note found from URL",
                    "source": _source_name(url),
                    "url": url,
                    "summary": "URL found by local search; text extraction by Ollama did not complete.",
                }
            )
        elif "/lit/gpn/" in lowered or "datasheet" in lowered or "/product" in lowered:
            output.components.append(
                {
                    "name": _source_name(url),
                    "type": "component_or_datasheet_url",
                    "key_specs": {},
                    "datasheet_url": url,
                }
            )
    output.key_specifications = [
        "Source URLs gathered successfully.",
        "Detailed facts not extracted because local Ollama extraction did not complete.",
    ]
    return output


def _is_low_quality_url(url: str) -> bool:
    lowered = url.lower()
    blocked = (
        "scribd.com",
        "textfiles.com",
        "stackexchange.com",
        "alldatasheet.com",
    )
    return any(domain in lowered for domain in blocked)


def _source_name(url: str) -> str:
    if "ti.com" in url:
        return "Texas Instruments"
    if "analog.com" in url:
        return "Analog Devices"
    if "vishay" in url:
        return "Vishay"
    if "susumu" in url:
        return "Susumu"
    if "caddock" in url:
        return "Caddock"
    if "bourns" in url:
        return "Bourns"
    return "source"
