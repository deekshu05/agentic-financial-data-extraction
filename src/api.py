"""FastAPI microservice exposing the financial-extraction agent workflow."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from src.graph import build_extraction_graph
from src.state import AgentState

app = FastAPI(title="Agentic Financial Data Extraction")
_graph = build_extraction_graph()


class ExtractRequest(BaseModel):
    document_text: str


@app.post("/extract")
def extract(request: ExtractRequest) -> dict:
    state = _graph.invoke(AgentState(document_text=request.document_text))
    return {
        "status": state.status,
        "extracted_fields": state.extracted_fields,
        "derived_metrics": state.derived_metrics,
        "validation_errors": state.validation_errors,
        "retries": state.retries,
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
