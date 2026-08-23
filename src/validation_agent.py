"""Validation node: checks extracted/derived data for completeness and sanity."""

from __future__ import annotations

from src.state import AgentState

REQUIRED_FIELDS = ("company", "revenue", "fiscal_period")


def validate_state(state: AgentState) -> AgentState:
    """Node: validate that required fields are present and sane."""
    errors: list[str] = []

    for field_name in REQUIRED_FIELDS:
        if field_name not in state.extracted_fields:
            errors.append(f"missing required field: {field_name}")

    revenue = state.extracted_fields.get("revenue")
    if revenue is not None and revenue < 0:
        errors.append("revenue must not be negative")

    state.validation_errors = errors
    state.status = "validated" if not errors else "failed"
    return state
