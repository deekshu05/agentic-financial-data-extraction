"""A minimal directed-graph executor for the financial-extraction agent.

Mirrors the node/edge/conditional-routing model popularized by LangGraph:
nodes are plain functions over a shared state object, edges determine
execution order, and conditional edges let the graph branch (e.g. retry
extraction) based on the current state. This keeps the workflow testable
and dependency-free while remaining a drop-in swap for a real LangGraph
`StateGraph` in production -- only `build_extraction_graph` would change.
"""

from __future__ import annotations

from typing import Callable

from src.state import AgentState

Node = Callable[[AgentState], AgentState]
Condition = Callable[[AgentState], str]

END = "__end__"


class AgentGraph:
    """A small state graph: named nodes, edges, and conditional branches."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._edges: dict[str, str] = {}
        self._conditional_edges: dict[str, tuple[Condition, dict[str, str]]] = {}
        self._entry_point: str | None = None

    def add_node(self, name: str, fn: Node) -> None:
        self._nodes[name] = fn

    def set_entry_point(self, name: str) -> None:
        self._entry_point = name

    def add_edge(self, from_node: str, to_node: str) -> None:
        self._edges[from_node] = to_node

    def add_conditional_edges(self, from_node: str, condition: Condition, mapping: dict[str, str]) -> None:
        self._conditional_edges[from_node] = (condition, mapping)

    def invoke(self, state: AgentState, max_steps: int = 20) -> AgentState:
        if self._entry_point is None:
            raise ValueError("Graph has no entry point; call set_entry_point() first.")

        current = self._entry_point
        for _ in range(max_steps):
            if current == END:
                return state

            node = self._nodes.get(current)
            if node is None:
                raise ValueError(f"Unknown node: {current}")
            state = node(state)

            if current in self._conditional_edges:
                condition, mapping = self._conditional_edges[current]
                branch = condition(state)
                current = mapping.get(branch, END)
            else:
                current = self._edges.get(current, END)

        raise RuntimeError(f"Graph did not terminate within {max_steps} steps")


def build_extraction_graph() -> AgentGraph:
    """Build the extract -> reason -> validate workflow, with one bounded
    retry back into extraction if validation fails."""
    from src.extraction_agent import extract_fields
    from src.reasoning_agent import compute_derived_metrics
    from src.validation_agent import validate_state

    graph = AgentGraph()
    graph.add_node("extract", extract_fields)
    graph.add_node("reason", compute_derived_metrics)
    graph.add_node("validate", validate_state)

    graph.set_entry_point("extract")
    graph.add_edge("extract", "reason")
    graph.add_edge("reason", "validate")

    def route_after_validate(state: AgentState) -> str:
        if state.status == "validated":
            return "done"
        if state.retries < 1:
            return "retry"
        return "done"

    def _retry(state: AgentState) -> AgentState:
        state.retries += 1
        return extract_fields(state)

    graph.add_node("retry_extract", _retry)
    graph.add_conditional_edges(
        "validate",
        route_after_validate,
        {"done": END, "retry": "retry_extract"},
    )
    graph.add_edge("retry_extract", "reason")

    return graph
