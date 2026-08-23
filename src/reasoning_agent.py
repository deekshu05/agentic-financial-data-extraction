"""Reasoning node: derives higher-level metrics from extracted fields."""

from __future__ import annotations

from src.state import AgentState


def compute_derived_metrics(state: AgentState) -> AgentState:
    """Node: compute derived metrics (e.g. net margin) from extracted fields."""
    fields = state.extracted_fields
    metrics: dict = {}

    revenue = fields.get("revenue")
    net_income = fields.get("net_income")
    if revenue and net_income is not None and revenue != 0:
        metrics["net_margin_pct"] = round((net_income / revenue) * 100, 2)

    if revenue is not None:
        metrics["revenue_flagged_low"] = revenue < 0

    state.derived_metrics = metrics
    state.status = "reasoned"
    return state
