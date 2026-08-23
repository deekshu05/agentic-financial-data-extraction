"""Extraction node: pulls structured financial fields out of unstructured text.

Uses regex-based extraction as a fast, dependency-free baseline. The same
node signature (AgentState -> AgentState) makes it easy to swap in an
LLM-backed extractor for documents that don't match these patterns.
"""

from __future__ import annotations

import re

from src.state import AgentState

_PATTERNS = {
    "company": re.compile(r"(?:Company|Issuer):\s*(.+)", re.IGNORECASE),
    "revenue": re.compile(r"Revenue[:\s]+\$?([\d,]+(?:\.\d+)?)\s*(million|billion)?", re.IGNORECASE),
    "net_income": re.compile(r"Net Income[:\s]+\$?([\d,]+(?:\.\d+)?)\s*(million|billion)?", re.IGNORECASE),
    "fiscal_period": re.compile(r"(Q[1-4]\s*\d{4}|FY\s*\d{4})", re.IGNORECASE),
}


def _to_number(raw: str, unit: str | None) -> float:
    value = float(raw.replace(",", ""))
    if unit and unit.lower() == "billion":
        value *= 1000  # normalize to millions
    return value


def extract_fields(state: AgentState) -> AgentState:
    """Node: extract structured fields from state.document_text."""
    text = state.document_text
    fields: dict = {}

    company_match = _PATTERNS["company"].search(text)
    if company_match:
        fields["company"] = company_match.group(1).strip()

    for key in ("revenue", "net_income"):
        match = _PATTERNS[key].search(text)
        if match:
            fields[key] = _to_number(match.group(1), match.group(2))

    period_match = _PATTERNS["fiscal_period"].search(text)
    if period_match:
        fields["fiscal_period"] = period_match.group(1).upper()

    state.extracted_fields = fields
    state.status = "extracted"
    return state
