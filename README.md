# OpenClaw Research Layer

OpenClaw is a fully local research and grounding layer for a future Electronics Engineering AI system.

It is designed to search for technical information, collect source URLs, read webpages or documents where possible, identify missing knowledge gaps, and return structured JSON. It is not a circuit design tool.

## Purpose

OpenClaw acts as the information layer before a future Electronics AI design layer.

Simple explanation:

```text
OpenClaw = research, sources, datasheets, gaps, JSON
Electronics AI = circuit design, component decisions, simulation, PCB
```

## What OpenClaw Can Do

- Accept electronics-related research prompts.
- Search the web using a local SearXNG instance.
- Prefer technical and official sources where possible.
- Collect datasheet, application note, article, and reference-document URLs.
- Fetch and clean readable webpage text.
- Send extracted text to a local Ollama model for structuring.
- Return a strict JSON output.
- Detect when a prompt is asking for design work.
- Identify likely missing information gaps.
- Explain which downstream engineering steps are blocked.

## What OpenClaw Must Not Do

- Design circuits.
- Select final components.
- Perform SPICE or ngspice simulation.
- Estimate final circuit performance.
- Generate PCB layouts.
- Generate KiCad or tscircuit output.
- Make engineering conclusions without sources.
- Invent missing datasheet values.

## Current Local Stack

| Item | Use |
| --- | --- |
| Python | Main application code |
| SearXNG | Local web search engine |
| Ollama | Local model server |
| qwen2.5:7b | Current local extraction model |
| Docker | Runs SearXNG and Ollama services |
| BeautifulSoup | HTML parsing |
| Trafilatura | Webpage text extraction |
| JSON | Structured output format |

## Architecture

```text
User Prompt
    |
    v
OpenClaw Guardrails
    |
    +--> Design prompt detected -> return research gaps only
    |
    v
SearXNG Local Search
    |
    v
Source URL Collection
    |
    v
Webpage / Document Text Extraction
    |
    v
Ollama Local Model Extraction
    |
    v
Strict JSON Research Output
    |
    v
Future Electronics AI Design Layer
```

## Main Commands

Run a normal research query:

```powershell
python -B -m openclaw "Find official datasheets and application notes for LM358"
```

Run general gap detection:

```powershell
python -B -m openclaw --detect-gaps "Design a low noise current source using zero drift op amps"
```

Run the built-in Entry 001 gap example:

```powershell
python -B -m openclaw --entry-001-gaps
```

Check local configuration and Ollama health:

```powershell
python -B -m openclaw --doctor
```

## Configuration

Settings are stored in `.env`.

Current important settings:

```text
SEARXNG_URL=http://localhost:8080
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OPENCLAW_MAX_RESULTS=8
OPENCLAW_TIMEOUT_SECONDS=120
OPENCLAW_MAX_SOURCE_BLOCKS=3
OPENCLAW_MAX_CHARS_PER_SOURCE=2500
OPENCLAW_OLLAMA_NUM_PREDICT=900
```

## Output Format

OpenClaw returns JSON with this structure:

```json
{
  "query": "",
  "summary": "",
  "key_concepts": [],
  "topologies_found": [],
  "reference_designs": [],
  "components": [],
  "application_notes": [],
  "engineering_constraints": [],
  "key_specifications": [],
  "source_urls": [],
  "limitations_or_missing_data": []
}
```

## Current Status

Working:

- Local Python CLI.
- SearXNG search connection.
- Source URL collection.
- Ollama health check.
- `.env` configuration loading.
- Design boundary guardrails.
- General prompt-level gap detection.
- Entry 001 Libbrecht-Hall gap report.
- JSON output generation.

Partially working:

- Webpage/document extraction.
- Ollama-based source summarization.
- Official source filtering.

Current known issue:

```text
SearXNG search works and URLs are collected.
Ollama is running and qwen2.5:7b is installed.
However, local extraction can time out when the model receives technical source text.
```

Current observed error:

```text
Ollama extraction failed:
HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=120)
```

Root cause:

```text
The local qwen2.5:7b model is taking longer than 120 seconds to process the extracted technical source content. This is a local performance and prompt-size limitation, not a search failure.
```

## Limitations

- This is an MVP research-layer scaffold, not a production research system yet.
- It does not include a real KG-2/KG-3 knowledge database.
- Gap detection is currently heuristic.
- It does not yet know which datasheets or app notes are already ingested.
- PDF extraction needs improvement.
- Some search results can be low quality.
- Official-source filtering needs to be made stronger.
- It does not calculate current noise.
- It does not design circuits.
- It does not choose final components.
- It does not generate schematics, PCB layouts, KiCad files, or simulations.

## Final Summary

OpenClaw is the first working local research and grounding layer for an Electronics AI system.

It can search, gather source URLs, identify gaps, enforce design boundaries, and return structured JSON. The next major improvement is to make document extraction and local model summarization faster and more reliable.

