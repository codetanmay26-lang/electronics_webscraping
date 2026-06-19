from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class GapItem:
    id: str
    category: str
    title: str
    can_identify: bool
    can_help_overcome: bool
    openclaw_action: str
    outside_openclaw: str
    priority: str
    source_targets: list[str] = field(default_factory=list)


@dataclass
class GapAssessment:
    entry_id: str
    status: str
    summary: str
    gaps: list[GapItem] = field(default_factory=list)
    openclaw_can_do: list[str] = field(default_factory=list)
    openclaw_must_not_do: list[str] = field(default_factory=list)

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent, ensure_ascii=True)


def entry_001_gap_assessment() -> GapAssessment:
    return GapAssessment(
        entry_id="Entry 001",
        status="research_layer_can_help_but_design_layer_still_blocked",
        summary=(
            "OpenClaw can identify the missing topology, datasheets, application notes, "
            "and noise-analysis source requirements. It can gather and structure the "
            "source-backed information. It cannot perform the circuit design, component "
            "selection, PCB generation, or current-noise estimate."
        ),
        openclaw_can_do=[
            "Find and retrieve official sources",
            "Extract datasheet specifications",
            "Extract application-note facts",
            "Create ingestion-ready KG-2 and KG-3 research JSON",
            "Report missing information as not found",
            "Preserve citations and source URLs",
        ],
        openclaw_must_not_do=[
            "Generate the Libbrecht-Hall circuit",
            "Select final components",
            "Estimate current noise",
            "Generate schematic, PCB, KiCad, or tscircuit output",
            "Make engineering conclusions not directly stated by sources",
        ],
        gaps=[
            GapItem(
                id="GAP-001-A",
                category="topology_gap",
                title="Libbrecht-Hall current source topology missing from KG-2",
                can_identify=True,
                can_help_overcome=True,
                openclaw_action="Retrieve and extract the original paper and precision-current-source app notes.",
                outside_openclaw="Circuit synthesis from the topology belongs to the Electronics AI.",
                priority="HIGH",
                source_targets=[
                    "Libbrecht & Hall 1993 Rev. Sci. Instrum. 64, 2133",
                    "TI SBOA327",
                    "TI SBOA273",
                    "ADI AN-1357",
                ],
            ),
            GapItem(
                id="GAP-001-B",
                category="component_gap",
                title="Zero-drift op-amp datasheets missing from KG-3",
                can_identify=True,
                can_help_overcome=True,
                openclaw_action="Retrieve official datasheets and extract offset, drift, noise, supply, and package data.",
                outside_openclaw="Final op-amp selection belongs to the Electronics AI or engineer.",
                priority="HIGH",
                source_targets=["OPA189", "ADA4522-2", "AD8628", "OPA2188"],
            ),
            GapItem(
                id="GAP-001-C",
                category="component_gap",
                title="Ultra-precision resistor datasheets missing from KG-3",
                can_identify=True,
                can_help_overcome=True,
                openclaw_action="Retrieve official resistor datasheets and extract tolerance, TCR, power, voltage, and package data.",
                outside_openclaw="Final sense-resistor choice belongs to the Electronics AI or engineer.",
                priority="MEDIUM",
                source_targets=["Vishay VSR", "Susumu RG2012N", "Caddock MP915"],
            ),
            GapItem(
                id="GAP-001-D",
                category="analysis_gap",
                title="Current-noise estimation missing from downstream pipeline",
                can_identify=True,
                can_help_overcome=True,
                openclaw_action="Collect source-backed formulas and datasheet noise parameters required by a future estimator.",
                outside_openclaw="Noise estimation calculations belong to an analysis module outside OpenClaw.",
                priority="HIGH",
                source_targets=[
                    "Johnson noise formula source",
                    "op-amp voltage noise density datasheet values",
                    "op-amp current noise density datasheet values",
                    "1/f noise or corner frequency source data",
                ],
            ),
            GapItem(
                id="GAP-001-E",
                category="component_gap",
                title="Precision potentiometer datasheets missing from KG-3",
                can_identify=True,
                can_help_overcome=True,
                openclaw_action="Retrieve official potentiometer datasheets and extract resistance range, tolerance, tempco, power, and adjustment data.",
                outside_openclaw="Final potentiometer selection belongs to the Electronics AI or engineer.",
                priority="LOW",
                source_targets=["Bourns 3590S", "Vishay P11"],
            ),
        ],
    )

