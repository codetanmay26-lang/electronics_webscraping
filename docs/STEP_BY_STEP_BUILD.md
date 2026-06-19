# Step-by-Step Build Plan

## Phase 1: Local Services

1. Install Docker Desktop or run services directly.
2. Start SearXNG locally on `http://localhost:8080`.
3. Start Ollama locally on `http://localhost:11434`.
4. Pull a local model, for example:

```powershell
ollama pull qwen3:32b
```

Use a smaller model first if your machine cannot run a 32B model comfortably.

## Phase 2: Search and Retrieval

1. Send the query to SearXNG.
2. Prefer official manufacturer domains.
3. Download top pages.
4. Extract readable text.
5. Keep source URL, title, and extracted text together.

## Phase 3: Structuring

1. Send only extracted source text to the local Ollama model.
2. Require strict JSON.
3. Validate the output with Pydantic.
4. Mark missing values as `not found`.
5. Preserve all important source URLs.

## Phase 4: Testing

1. Test guardrails with prohibited prompts.
2. Test offline behavior when SearXNG is unavailable.
3. Test extraction on known official datasheets and application notes.
4. Save sample outputs for regression checks.

## Phase 5: Integration

Expose OpenClaw as one of:

- CLI module
- Local FastAPI service
- Message queue worker
- Python library imported by the downstream Electronics AI

The downstream Electronics AI can consume the JSON output, but OpenClaw should never
perform design decisions itself.

