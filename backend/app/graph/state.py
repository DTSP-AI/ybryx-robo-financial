"""Shared state definitions for LangGraph workflows."""

from typing import Annotated, Any, Sequence
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State for agent workflows.

    Uses add_messages reducer for message list.
    """

    # Messages
    messages: Annotated[Sequence[dict[str, Any]], add_messages]

    # Routing
    next_agent: str
    current_agent: str

    # Context
    application_id: str | None
    user_id: str | None
    tenant_id: str | None

    # Data
    application_data: dict[str, Any] | None
    financial_analysis: dict[str, Any] | None
    dealer_matches: list[dict[str, Any]] | None
    equipment_recommendations: list[dict[str, Any]] | None

    # Memory
    memory_context: list[dict[str, Any]] | None

    # Control
    iteration_count: int
    max_iterations: int
    error: str | None
    completed: bool
