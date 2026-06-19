from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ReferenceDesign:
    title: str = ""
    source: str = ""
    url: str = ""
    summary: str = ""


@dataclass
class Component:
    name: str = ""
    type: str = ""
    key_specs: dict[str, Any] = field(default_factory=dict)
    datasheet_url: str = ""


@dataclass
class ApplicationNote:
    title: str = ""
    source: str = ""
    url: str = ""
    summary: str = ""


@dataclass
class ResearchOutput:
    query: str = ""
    summary: str = ""
    key_concepts: list[str] = field(default_factory=list)
    topologies_found: list[str] = field(default_factory=list)
    reference_designs: list[ReferenceDesign] = field(default_factory=list)
    components: list[Component] = field(default_factory=list)
    application_notes: list[ApplicationNote] = field(default_factory=list)
    engineering_constraints: list[str] = field(default_factory=list)
    key_specifications: list[str] = field(default_factory=list)
    source_urls: list[str] = field(default_factory=list)
    limitations_or_missing_data: list[str] = field(default_factory=list)

    def model_dump(self) -> dict[str, Any]:
        return asdict(self)

    def model_dump_json(self, indent: int | None = None) -> str:
        return json.dumps(self.model_dump(), indent=indent, ensure_ascii=True)

    @classmethod
    def model_validate_json(cls, raw: str) -> "ResearchOutput":
        data = json.loads(raw)
        data["reference_designs"] = [
            ReferenceDesign(**item) for item in data.get("reference_designs", [])
        ]
        data["components"] = [Component(**item) for item in data.get("components", [])]
        data["application_notes"] = [
            ApplicationNote(**item) for item in data.get("application_notes", [])
        ]
        return cls(**data)


def empty_research_output(query: str, limitation: str) -> ResearchOutput:
    return ResearchOutput(
        query=query,
        summary="",
        limitations_or_missing_data=[limitation],
    )
