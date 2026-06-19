from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from openclaw.guardrails import is_prohibited_request


@dataclass
class DetectedRequirement:
    category: str
    requirement: str
    evidence: str


@dataclass
class MissingInformation:
    category: str
    description: str
    why_needed: str
    research_task: str
    priority: str


@dataclass
class GapDetectionResult:
    prompt: str
    status: str
    detected_requirements: list[DetectedRequirement] = field(default_factory=list)
    missing_information: list[MissingInformation] = field(default_factory=list)
    research_tasks_needed: list[str] = field(default_factory=list)
    blocked_downstream_steps: list[str] = field(default_factory=list)
    openclaw_can_do: list[str] = field(default_factory=list)
    openclaw_must_not_do: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent, ensure_ascii=True)


RULES: tuple[dict[str, Any], ...] = (
    {
        "category": "topology",
        "patterns": ("topology", "architecture", "libbrecht", "hall", "flyback", "buck", "boost", "current source"),
        "description": "Topology or circuit architecture source material may be needed.",
        "why_needed": "Downstream design cannot use an architecture unless its source-backed behavior and constraints are known.",
        "research_task": "Find official papers, application notes, or reference designs for the requested topology.",
        "priority": "HIGH",
        "blocked_step": "schematic_generation",
    },
    {
        "category": "component_datasheet",
        "patterns": ("opamp", "op-amp", "zero drift", "ldo", "mosfet", "resistor", "potentiometer", "capacitor", "inductor", "diode", "adc", "dac"),
        "description": "Component datasheets and specifications may be missing.",
        "why_needed": "Specific electrical limits, packages, supply ranges, noise values, tolerances, and ratings must come from datasheets.",
        "research_task": "Find official manufacturer datasheets for every named or implied component type.",
        "priority": "HIGH",
        "blocked_step": "bom_generation",
    },
    {
        "category": "power_requirements",
        "patterns": ("power supply", "single dc input", "polarity", "polarities", "voltage rail", "ldo", "regulator", "supply"),
        "description": "Power input, generated rails, regulator requirements, and polarity data may be missing.",
        "why_needed": "Downstream design needs source-backed supply limits and regulator requirements before creating a power tree.",
        "research_task": "Find datasheets and application notes covering required supply rails, regulator limits, and operating ranges.",
        "priority": "HIGH",
        "blocked_step": "power_tree_generation",
    },
    {
        "category": "performance_analysis",
        "patterns": ("noise", "stability", "thermal", "drift", "accuracy", "ripple", "bandwidth", "estimate"),
        "description": "Performance formulas and datasheet parameters may be missing.",
        "why_needed": "Calculations require sourced equations, user assumptions, and datasheet parameters.",
        "research_task": "Find source-backed formulas and datasheet parameters for the requested performance estimate.",
        "priority": "HIGH",
        "blocked_step": "analysis_or_estimation",
    },
    {
        "category": "reference_design",
        "patterns": ("reference design", "eval board", "evaluation board", "application note", "app note"),
        "description": "Reference designs or application notes may be needed.",
        "why_needed": "Reference designs and app notes provide source-backed implementation examples for downstream systems.",
        "research_task": "Find official reference designs, evaluation-board documents, and application notes.",
        "priority": "MEDIUM",
        "blocked_step": "implementation_guidance",
    },
    {
        "category": "simulation",
        "patterns": ("simulate", "spice", "ngspice", "model", "transient", "ac analysis"),
        "description": "Simulation model availability may be unknown.",
        "why_needed": "Simulation requires vendor models and analysis setup outside the research layer.",
        "research_task": "Find official SPICE or simulation models and model documentation.",
        "priority": "MEDIUM",
        "blocked_step": "simulation",
    },
    {
        "category": "pcb_or_output",
        "patterns": ("pcb", "kicad", "layout", "gerber", "tscircuit", "3d model"),
        "description": "PCB/layout output requirements are outside OpenClaw and may need downstream tooling.",
        "why_needed": "PCB generation requires engineering decisions and CAD output generation outside the research layer.",
        "research_task": "Find layout guidelines, package drawings, and manufacturer footprint recommendations.",
        "priority": "MEDIUM",
        "blocked_step": "pcb_generation",
    },
    {
        "category": "bom_or_selection",
        "patterns": ("component list", "bom", "list of components", "choose", "select", "best"),
        "description": "Final component selection is requested or implied.",
        "why_needed": "OpenClaw can collect candidates and specifications, but final selection is an engineering decision.",
        "research_task": "Find official datasheets and comparison-relevant specs for candidate component classes.",
        "priority": "HIGH",
        "blocked_step": "component_selection",
    },
)


def detect_gaps(prompt: str) -> GapDetectionResult:
    normalized = _normalize(prompt)
    requirements = _detect_requirements(prompt, normalized)
    missing = _missing_info_from_requirements(requirements)
    research_tasks = _unique(item.research_task for item in missing)
    blocked_steps = _unique(item.research_task and _blocked_step_for_category(item.category) for item in missing)

    status = "research_gaps_detected"
    limitations = [
        "This is heuristic prompt-level gap detection.",
        "It does not yet compare against a real KG-2/KG-3 inventory.",
        "A downstream knowledge-base check is required to know whether each item is already ingested.",
    ]
    if is_prohibited_request(prompt):
        status = "research_gaps_detected_design_request_outside_openclaw"
        limitations.append("The prompt asks for work outside OpenClaw's research-only boundary.")

    return GapDetectionResult(
        prompt=prompt,
        status=status,
        detected_requirements=requirements,
        missing_information=missing,
        research_tasks_needed=research_tasks,
        blocked_downstream_steps=blocked_steps,
        openclaw_can_do=[
            "Identify likely missing information from the prompt",
            "Create research tasks for missing sources",
            "Search official sources, datasheets, papers, application notes, and reference designs",
            "Extract source-backed facts and return structured JSON",
            "Report missing information as not found",
        ],
        openclaw_must_not_do=[
            "Design circuits",
            "Select final components",
            "Run simulations",
            "Estimate final performance",
            "Generate PCB or schematic outputs",
        ],
        limitations=limitations,
    )


def _detect_requirements(prompt: str, normalized: str) -> list[DetectedRequirement]:
    requirements: list[DetectedRequirement] = []
    for rule in RULES:
        evidence = _first_match(normalized, rule["patterns"])
        if evidence:
            requirements.append(
                DetectedRequirement(
                    category=rule["category"],
                    requirement=rule["description"],
                    evidence=evidence,
                )
            )

    numeric_specs = re.findall(r"\b\d+(?:\.\d+)?\s*(?:ma|a|mv|v|uv|db|hz|khz|mhz|ohm|k|m|%)\b", normalized)
    for spec in _unique(numeric_specs):
        requirements.append(
            DetectedRequirement(
                category="explicit_specification",
                requirement=f"Explicit numeric requirement found: {spec}",
                evidence=spec,
            )
        )
    return requirements


def _missing_info_from_requirements(requirements: list[DetectedRequirement]) -> list[MissingInformation]:
    missing: list[MissingInformation] = []
    seen: set[str] = set()
    rules_by_category = {rule["category"]: rule for rule in RULES}
    for requirement in requirements:
        if requirement.category == "explicit_specification":
            continue
        if requirement.category in seen:
            continue
        seen.add(requirement.category)
        rule = rules_by_category[requirement.category]
        missing.append(
            MissingInformation(
                category=requirement.category,
                description=rule["description"],
                why_needed=rule["why_needed"],
                research_task=rule["research_task"],
                priority=rule["priority"],
            )
        )
    if not missing:
        missing.append(
            MissingInformation(
                category="general_research",
                description="No specific electronics gap category was detected.",
                why_needed="The prompt may still need source-backed research before downstream use.",
                research_task="Search official and reliable sources for the prompt and extract relevant technical facts.",
                priority="MEDIUM",
            )
        )
    return missing


def _blocked_step_for_category(category: str) -> str:
    for rule in RULES:
        if rule["category"] == category:
            return str(rule["blocked_step"])
    return "unknown_downstream_step"


def _first_match(normalized: str, patterns: tuple[str, ...]) -> str:
    for pattern in patterns:
        if pattern in normalized:
            return pattern
    return ""


def _normalize(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def _unique(items: Any) -> list[str]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        values.append(str(item))
    return values

