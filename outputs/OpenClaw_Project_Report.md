# OpenClaw Research Layer - Project Report

Date: 2026-06-19

## 1. Project Overview

OpenClaw Research Layer is a fully local research and grounding system created for a future Electronics Engineering AI system.

The purpose of OpenClaw is simple:

```text
Collect technical information.
Identify missing knowledge.
Structure the information into JSON.
Pass it to a future Electronics AI.
```

OpenClaw is not designed to perform electronics design itself. It is only the research layer.

Simple role separation:

```text
OpenClaw = eyes and library
Electronics AI = engineering brain
```

## 2. Main Objective

The objective was to build a local system that can:

- Search for technical information.
- Gather datasheets, application notes, papers, and source URLs.
- Extract technical content from web sources where possible.
- Identify missing information gaps.
- Return structured JSON.
- Work locally without cloud APIs.

The system was also required to avoid engineering design work.

## 3. What Has Been Achieved

The following parts have been built:

- A local Python project named `OpenClaw`.
- A command-line interface that can be run from VS Code PowerShell.
- Local SearXNG integration for web search.
- Local Ollama integration for model-based extraction.
- Configuration through `.env`.
- Strict JSON output format.
- Design guardrails.
- General gap detection for any electronics prompt.
- A special Entry 001 gap report for the Libbrecht-Hall current source prompt.
- Source URL collection from web search.
- A diagnostic command to check local model settings.
- Professional project documentation.

Current working commands include:

```powershell
python -B -m openclaw "your research query"
python -B -m openclaw --detect-gaps "your electronics prompt"
python -B -m openclaw --entry-001-gaps
python -B -m openclaw --doctor
```

## 4. What OpenClaw Does

OpenClaw does these tasks:

- Accepts a user query.
- Checks whether the query is research or design.
- If it is a design request, it does not design.
- If it is a design request, it identifies research gaps instead.
- If it is a research request, it searches the web using SearXNG.
- Collects source URLs.
- Attempts to read and clean webpage content.
- Sends extracted source text to a local Ollama model.
- Returns structured JSON.

Example research request:

```text
Find official datasheets and application notes for zero drift op amps.
```

Example design request:

```text
Design a low noise current source.
```

For the design request, OpenClaw will not design the circuit. It will report what research information is missing.

## 5. What OpenClaw Does Not Do

OpenClaw does not:

- Design circuits.
- Select final components.
- Estimate final current noise.
- Perform SPICE simulation.
- Generate PCB layouts.
- Generate KiCad files.
- Generate tscircuit files.
- Optimize circuit performance.
- Invent missing datasheet values.
- Make engineering conclusions without sources.

This is intentional. OpenClaw is only the research and grounding layer.

## 6. System Architecture

The current system flow is:

```text
User Prompt
    |
    v
OpenClaw CLI
    |
    v
Guardrail Check
    |
    +--> Design Prompt -> Gap Report JSON
    |
    v
Research Prompt
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
Ollama Local Model
    |
    v
Structured JSON Output
    |
    v
Future Electronics AI
```

## 7. Technologies Used

| Technology | Purpose |
| --- | --- |
| Python | Main programming language |
| SearXNG | Local search engine |
| Ollama | Local model runner |
| qwen2.5:7b | Current local language model |
| Docker | Runs SearXNG and Ollama |
| BeautifulSoup | Parses HTML |
| Trafilatura | Extracts clean webpage text |
| JSON | Output format |
| VS Code PowerShell | User execution environment |

No cloud API is required for the intended architecture.

## 8. Model Used

The current local model is:

```text
qwen2.5:7b
```

It is served by Ollama at:

```text
http://localhost:11434
```

The model was confirmed installed through:

```powershell
python -B -m openclaw --doctor
```

The doctor command showed:

```text
ollama_model = qwen2.5:7b
Ollama /api/tags = working
```

## 9. Search Engine Used

The local search engine is SearXNG.

It runs at:

```text
http://localhost:8080
```

It is configured to return JSON search results so Python can process them.

## 10. Output Format

OpenClaw returns strict JSON.

Main fields:

```text
query
summary
key_concepts
topologies_found
reference_designs
components
application_notes
engineering_constraints
key_specifications
source_urls
limitations_or_missing_data
```

This makes the output easy for another AI system to consume.

## 11. File-by-File Explanation

### `README.md`

Professional project overview.

It explains:

- What OpenClaw is.
- What it can do.
- What it must not do.
- How to run it.
- Current limitations.
- Current known error.

### `requirements.txt`

Lists Python dependencies:

```text
beautifulsoup4
requests
trafilatura
```

These libraries help with web requests, HTML parsing, and text extraction.

### `.env`

Stores local configuration.

Current key settings:

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

This file tells OpenClaw which local services and model to use.

### `.env.example`

Template configuration file.

It can be copied to `.env` on another machine.

### `local-services.example.yml`

Docker Compose file.

It defines local services:

- `openclaw-searxng`
- `openclaw-ollama`

### `work/searxng/settings.yml`

SearXNG configuration.

It enables JSON output:

```text
html
json
```

Without this, SearXNG may reject JSON search requests.

### `openclaw/__init__.py`

Marks the folder as a Python package.

It also contains the project version.

### `openclaw/__main__.py`

Command-line entry point.

It allows:

```powershell
python -B -m openclaw "query"
```

It also provides:

```powershell
--detect-gaps
--entry-001-gaps
--doctor
```

### `openclaw/config.py`

Loads settings from `.env`.

It reads:

- SearXNG URL.
- Ollama URL.
- Ollama model.
- Search result limit.
- Timeout.
- Source chunk size.
- Ollama output limit.

### `openclaw/schema.py`

Defines the JSON output structure.

It ensures output always has the same fields.

This is important because a future Electronics AI can reliably read the result.

### `openclaw/guardrails.py`

Contains design safety rules.

It detects terms such as:

```text
design
simulate
optimize
choose component
PCB layout
SPICE
```

If the user asks for these tasks, OpenClaw avoids engineering work.

### `openclaw/search.py`

Connects to SearXNG.

It sends search queries and collects results.

It also gives higher ranking to official electronics sources such as:

- Texas Instruments
- Analog Devices
- ST
- Infineon
- Microchip
- onsemi
- NXP
- Renesas
- Vishay
- Mouser
- DigiKey

### `openclaw/fetch.py`

Fetches webpages and extracts readable text.

It uses:

- `requests`
- `BeautifulSoup`
- `trafilatura`

Its job is to remove noise and keep technical content where possible.

### `openclaw/extract.py`

Sends extracted source text to the local Ollama model.

It instructs the model:

- Return JSON only.
- Do not design circuits.
- Do not choose final components.
- Do not infer missing values.
- Only summarize source-backed facts.

### `openclaw/pipeline.py`

Main workflow file.

It coordinates:

```text
guardrails
search
fetch
extract
fallback output
```

If the prompt is a design prompt, it returns gap information instead of a design.

If Ollama extraction fails, it returns source URLs and limitations.

### `openclaw/gap_detector.py`

General gap detection module.

It can analyze any electronics prompt and detect likely gaps such as:

- Topology gap.
- Component datasheet gap.
- Power supply gap.
- Performance analysis gap.
- Reference design gap.
- Simulation gap.
- PCB/output gap.
- BOM or component selection gap.

It returns research tasks and blocked downstream steps.

### `openclaw/gap_schema.py`

Special gap report for Entry 001.

Entry 001 is the Libbrecht-Hall precision current source prompt.

It identifies:

- Libbrecht-Hall topology missing.
- Zero-drift op-amp datasheets missing.
- Ultra-precision resistor datasheets missing.
- Noise estimator missing.
- Precision potentiometer datasheets missing.

### `docs/BOUNDARIES.md`

Explains what OpenClaw is allowed to do and forbidden to do.

### `docs/STEP_BY_STEP_BUILD.md`

Explains setup steps in order.

It includes:

- Python setup.
- Docker setup.
- SearXNG.
- Ollama.
- Model pull.
- Running OpenClaw.

### `docs/GAP_HANDLING.md`

Explains how OpenClaw handles gaps.

It explains what OpenClaw can identify and what must be handled by the future Electronics AI.

### `outputs/OpenClaw_Project_Report.md`

This project report.

It is written for simple explanation and authority review.

## 12. Important Code Logic in Simple Words

The main logic is:

```text
Load settings.
Read user query.
Check if it asks for design.
If design, return gap report.
If research, search web through SearXNG.
Collect URLs.
Try to read pages.
Send readable text to Ollama.
Return JSON.
If extraction fails, return source URLs and error reason.
```

This gives a safe research layer before engineering work begins.

## 13. Example: Design Prompt Behavior

Input:

```text
Design a ultra low noise and highly stable current source for 100mA current range using Libbrecht Hall design...
```

OpenClaw response:

```text
This is a design-style request.
OpenClaw will not design the circuit.
It identifies required research and missing gaps.
```

Detected gaps include:

- Topology source material needed.
- Component datasheets needed.
- Power supply and LDO information needed.
- Noise formulas and noise parameters needed.
- BOM/component selection information needed.

Blocked downstream steps:

- Schematic generation.
- BOM generation.
- Power tree generation.
- Noise analysis.
- Component selection.

## 14. Example: Research Prompt Behavior

Input:

```text
Find official datasheets and application notes for Libbrecht Hall precision current source, zero drift op amps, ultra precision resistors, LDOs, and potentiometers
```

Observed output:

```text
Web search completed.
Source URLs were gathered.
Local model extraction did not complete.
URL-level research packet was returned.
```

Collected URLs included:

- Texas Instruments application note PDF.
- Renesas component page.
- Core academic PDF.
- ScienceDirect article page.
- Other search results.

![alt text](image.png)

## 15. Current Error

The current error is:

```text
Ollama extraction failed:
HTTPConnectionPool(host='localhost', port=11434): Read timed out. (read timeout=120)
```

## 16. Root Cause of Current Error

The root cause is:

```text
The local search step is working.
The local Ollama server is working.
The qwen2.5:7b model is installed.
But the model is taking longer than 120 seconds to process the technical source text.
```

This means the error is not because SearXNG is broken.

It is also not because Ollama is missing.

The issue is mainly:

- The local model is slow on the current machine.
- Technical sources can be large.
- PDF/webpage content is difficult to extract cleanly.
- Some sources are noisy.
- The extraction task may still be too heavy for the current timeout.

## 17. Current Working Status

Working:

- Python CLI runs.
- `.env` settings load.
- Docker services are being used.
- SearXNG search works.
- Source URLs are collected.
- Ollama server is reachable.
- qwen2.5:7b model is installed.
- Gap detection works.
- Design guardrails work.
- JSON output works.

Partially working:

- Webpage/PDF text extraction.
- Ollama source summarization.
- Official-source filtering.

Not built yet:

- Production-grade PDF extraction.
- Real KG-2/KG-3 knowledge base.
- Already-ingested document tracking.
- Noise estimator.
- Circuit design layer.
- Component selection layer.
- Simulation layer.
- PCB generation layer.

## 18. Limitations

Current limitations are:

- This is an MVP, not a final production system.
- Gap detection is heuristic.
- It does not yet compare prompts against a real knowledge base.
- It cannot say with certainty whether a datasheet is already ingested.
- Some search results are not official or not high quality.
- PDF extraction needs stronger tooling.
- Ollama extraction can time out.
- It does not design circuits.
- It does not estimate current noise.
- It does not choose final parts.
- It does not generate KiCad, PCB, or simulation files.

## 19. What Has Been Proved

This project proves that:

- A local research layer can be built.
- SearXNG can provide local web search.
- Ollama can provide a local model endpoint.
- OpenClaw can separate research from design.
- OpenClaw can identify missing information gaps.
- OpenClaw can return structured JSON.
- OpenClaw can act as a safe front layer before an Electronics AI.

## 20. Next Recommended Improvements

Recommended next steps:

1. Add stronger official-source filtering.
2. Add better PDF extraction.
3. Reduce Ollama prompt size further.
4. Add source-by-source summarization instead of sending multiple sources at once.
5. Add local storage for downloaded documents.
6. Add a small knowledge base to track ingested sources.
7. Add tests using known datasheets and application notes.
8. Later connect the output to a separate Electronics AI design layer.

## 21. Simple Final Explanation

In simple words:

```text
We built the first local version of OpenClaw.

It is a research and grounding layer for electronics AI.

It searches technical sources, collects URLs, identifies missing information,
protects against accidental design work, and outputs structured JSON.

It runs locally using SearXNG and Ollama with qwen2.5:7b.

The current blocker is that the local model sometimes takes too long to extract
technical information from source text, causing a 120-second timeout.

The design layer is not built yet. OpenClaw is only the research layer.
```

## 22. Conclusion

OpenClaw has successfully reached MVP stage as a local research and grounding subsystem.

It is not a complete electronics design AI. It is the foundation layer that prepares source-backed research for a future design AI.

The main achievement is safe separation between research and engineering design, with local search, local model usage, gap detection, and structured JSON output.

