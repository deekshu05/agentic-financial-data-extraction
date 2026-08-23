"""Shared state passed between nodes in the financial-extraction agent graph."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class AgentState:
    """Mutable state threaded through every node of the agent workflow."""

    document_text: str
    extracted_fields: dict = field(default_factory=dict)
    derived_metrics: dict = field(default_factory=dict)
    validation_errors: list[str] = field(default_factory=list)
    retries: int = 0
    status: str = "pending"  # pending -> extracted -> reasoned -> validated | failed
