# Gap Handling for Entry 001

OpenClaw can help with Entry 001, but only as the research and grounding layer.

It can identify missing knowledge, gather source documents, extract facts, cite URLs, and
produce ingestion-ready JSON. It must not perform the circuit design, BOM decision, PCB
generation, or current-noise calculation itself.

## What OpenClaw Can Do

| Gap | Can OpenClaw identify it? | Can OpenClaw help overcome it? | Boundary |
| --- | --- | --- | --- |
| GAP-001-A Libbrecht-Hall topology missing | Yes | Yes, by finding and extracting the paper/app notes | It cannot synthesize the circuit |
| GAP-001-B zero-drift op-amp datasheets missing | Yes | Yes, by retrieving official datasheets and specs | It cannot choose the final op-amp |
| GAP-001-C ultra-precision resistor datasheets missing | Yes | Yes, by retrieving official datasheets and specs | It cannot choose the final sense resistor |
| GAP-001-D current noise estimation missing | Yes | Partly, by collecting equations and datasheet noise parameters | The estimator belongs to the Electronics AI or analysis layer |
| GAP-001-E potentiometer datasheets missing | Yes | Yes, by retrieving official datasheets and specs | It cannot choose the final potentiometer |

## Required OpenClaw Additions

To support entries like this properly, OpenClaw needs these research-layer features:

1. Gap detection schema. The starter implementation is `openclaw/gap_detector.py`.
2. Source target list for each gap.
3. Official-source retrieval rules.
4. Datasheet/application-note extraction.
5. Ingestion packet output for KG-2 and KG-3.
6. A clear `blocked_design_reason` field when downstream design is not ready.

## General Gap Detection

Run prompt-level gap detection with:

```powershell
python -m openclaw --detect-gaps "your electronics prompt here"
```

The detector returns JSON with:

- detected requirements
- likely missing information
- research tasks needed
- downstream steps that are blocked
- what OpenClaw can do
- what OpenClaw must not do

The current detector is heuristic. It does not yet compare the prompt against a real
KG-2/KG-3 inventory, so it should be treated as a first-pass gap report.

## What Belongs Outside OpenClaw

These items should not be implemented inside OpenClaw:

- `src/analysis/noise_estimator.py`
- `NoiseAnalysisResult`
- Documentation sections that present calculated design noise
- BOM final part selection
- Schematic synthesis
- PCB layout

OpenClaw may collect source-backed inputs for those modules, such as:

- resistor Johnson-noise formula from a reliable reference
- op-amp voltage noise density from datasheets
- op-amp current noise density from datasheets
- bandwidth assumptions stated by the user or source
- source URLs for every extracted parameter

The downstream Electronics AI or analysis layer should perform the calculation.

## Entry 001 Research Tasks

OpenClaw should create separate research jobs:

1. `Libbrecht Hall precision current source topology official paper application notes`
2. `TI SBOA327 precision current source design application note`
3. `TI SBOA273 low noise current source techniques application note`
4. `ADI AN-1357 precision current sources and sinks`
5. `OPA189 official datasheet TI zero drift op amp`
6. `ADA4522-2 official datasheet Analog Devices zero drift op amp`
7. `AD8628 official datasheet Analog Devices chopper stabilized op amp`
8. `OPA2188 official datasheet TI zero drift op amp`
9. `Vishay VSR precision resistor official datasheet`
10. `Susumu RG2012N precision resistor official datasheet`
11. `Caddock MP915 precision power resistor official datasheet`
12. `Bourns 3590S potentiometer official datasheet`
13. `Vishay P11 potentiometer official datasheet`

Each job should return strict JSON and preserve URLs.
