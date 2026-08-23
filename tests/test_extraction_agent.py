from src.extraction_agent import extract_fields
from src.state import AgentState


def test_extracts_company_and_revenue():
    text = (
        "Company: Acme Robotics Inc.\n"
        "Fiscal Period: Q3 2025\n"
        "Revenue: $120.5 million\n"
        "Net Income: $18.2 million\n"
    )
    state = AgentState(document_text=text)

    result = extract_fields(state)

    assert result.extracted_fields["company"] == "Acme Robotics Inc."
    assert result.extracted_fields["revenue"] == 120.5
    assert result.extracted_fields["net_income"] == 18.2
    assert result.extracted_fields["fiscal_period"] == "Q3 2025"
    assert result.status == "extracted"


def test_normalizes_billions_to_millions():
    text = "Company: Big Corp\nFiscal Period: FY2024\nRevenue: $2.1 billion\n"
    state = AgentState(document_text=text)

    result = extract_fields(state)

    assert result.extracted_fields["revenue"] == 2100.0


def test_handles_missing_fields_gracefully():
    state = AgentState(document_text="No structured data here.")

    result = extract_fields(state)

    assert result.extracted_fields == {}
    assert result.status == "extracted"
