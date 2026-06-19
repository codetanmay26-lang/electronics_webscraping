# OpenClaw Boundary Rules

OpenClaw is an information layer. It gathers and structures source-backed facts.

## Allowed

- Search for technical sources.
- Fetch official datasheets.
- Fetch manufacturer application notes.
- Extract reference design descriptions.
- Extract component specifications.
- Preserve source URLs.
- State missing information as not found.
- Return strict JSON.

## Forbidden

- Circuit design.
- Component selection decisions.
- Simulation or SPICE analysis.
- Optimization.
- PCB layout.
- Engineering conclusions beyond source text.
- Filling in missing datasheet values from memory.

## Enforcement Points

1. Reject prohibited user requests before search.
2. Use extraction prompts that explicitly forbid engineering reasoning.
3. Validate output against the JSON schema.
4. Keep citations and source URLs in every research result.
5. Send final decisions to a separate Electronics AI layer.

