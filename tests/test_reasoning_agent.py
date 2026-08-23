from src.reasoning_agent import compute_derived_metrics
from src.state import AgentState


def test_computes_net_margin():
    state = AgentState(document_text="")
    state.extracted_fields = {"revenue": 100.0, "net_income": 20.0}

    result = compute_derived_metrics(state)

    assert result.derived_metrics["net_margin_pct"] == 20.0
    assert result.status == "reasoned"


def test_flags_negative_revenue():
    state = AgentState(document_text="")
    state.extracted_fields = {"revenue": -5.0}

    result = compute_derived_metrics(state)

    assert result.derived_metrics["revenue_flagged_low"] is True


def test_no_margin_when_income_missing():
    state = AgentState(document_text="")
    state.extracted_fields = {"revenue": 100.0}

    result = compute_derived_metrics(state)

    assert "net_margin_pct" not in result.derived_metrics
