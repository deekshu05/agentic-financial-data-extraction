from src.graph import build_extraction_graph
from src.state import AgentState


def test_full_pipeline_validates_complete_document():
    text = (
        "Company: Acme Robotics Inc.\n"
        "Fiscal Period: Q3 2025\n"
        "Revenue: $120.5 million\n"
        "Net Income: $18.2 million\n"
    )
    graph = build_extraction_graph()
    state = graph.invoke(AgentState(document_text=text))

    assert state.status == "validated"
    assert state.validation_errors == []
    assert "net_margin_pct" in state.derived_metrics


def test_pipeline_retries_then_fails_on_incomplete_document():
    graph = build_extraction_graph()
    state = graph.invoke(AgentState(document_text="Nothing useful here."))

    assert state.status == "failed"
    assert state.retries == 1
    assert len(state.validation_errors) > 0
