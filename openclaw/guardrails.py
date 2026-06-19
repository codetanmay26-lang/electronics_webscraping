from __future__ import annotations


PROHIBITED_TERMS = {
    "design a circuit",
    "design an",
    "design a",
    "make a circuit",
    "create a circuit",
    "simulate",
    "spice",
    "ngspice",
    "optimize",
    "best component",
    "choose component",
    "select component",
    "pcb layout",
    "kicad layout",
    "generate pcb",
}


def is_prohibited_request(query: str) -> bool:
    normalized = " ".join(query.lower().split())
    if normalized.startswith(("design ", "build a circuit", "create a circuit", "make a circuit")):
        return True
    return any(term in normalized for term in PROHIBITED_TERMS)


def guardrail_message() -> str:
    return (
        "Request rejected by OpenClaw boundary: this layer only gathers, verifies, "
        "extracts, cites, and structures technical information. It does not design, "
        "simulate, optimize, select final components, or generate PCB layouts."
    )
