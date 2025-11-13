"""Supervisor agent for orchestrating specialist agents."""

from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from app.config import settings
from app.graph.state import AgentState

logger = structlog.get_logger()


# Supervisor routing options
members = ["financing", "dealer_matching", "knowledge", "FINISH"]
RouterResponse = Literal["financing", "dealer_matching", "knowledge", "FINISH"]


# System prompt for supervisor
SUPERVISOR_PROMPT = """You are a supervisor agent for Ybryx Capital's robotics financing platform.

Your role is to route user requests to the appropriate specialist agent:

1. **financing** - Handles prequalification applications, financial scoring, risk assessment, and lease term calculations
2. **dealer_matching** - Finds and matches authorized dealers based on location and equipment needs
3. **knowledge** - Provides information about robots, equipment specs, industry use cases, and general questions

Analyze the user's request and determine which agent should handle it. Consider:
- If it's about applying for financing or prequalification → financing
- If it's about finding dealers or local partners → dealer_matching
- If it's about robot specs, industries, or general info → knowledge
- If the request has been fully handled → FINISH

Current context:
- Application ID: {application_id}
- Previous agent: {current_agent}
- Iteration: {iteration_count}/{max_iterations}

Available agents: {members}

Based on the conversation, route to the next agent or FINISH if complete.
"""


def create_supervisor_node() -> callable:
    """Create the supervisor node function.

    Returns:
        callable: Supervisor node function
    """
    # Initialize supervisor LLM (OpenAI GPT-5-nano for fast routing)
    llm = ChatOpenAI(
        model=settings.openai_supervisor_model,
        temperature=0.1,  # Low temperature for consistent routing
        api_key=settings.openai_api_key,
        organization=settings.openai_org_id,
    )

    def supervisor_node(state: AgentState) -> AgentState:
        """Supervisor decides which agent to route to next.

        Args:
            state: Current agent state

        Returns:
            AgentState: Updated state with routing decision
        """
        messages = state["messages"]
        iteration_count = state.get("iteration_count", 0)
        max_iterations = state.get("max_iterations", 10)

        # Check iteration limit
        if iteration_count >= max_iterations:
            logger.warning(
                "max_iterations_reached",
                iteration=iteration_count,
                application_id=state.get("application_id"),
            )
            return {
                **state,
                "next_agent": "FINISH",
                "error": "Maximum iterations reached",
                "completed": True,
            }

        # Build supervisor prompt
        prompt = SUPERVISOR_PROMPT.format(
            application_id=state.get("application_id", "None"),
            current_agent=state.get("current_agent", "None"),
            iteration_count=iteration_count,
            max_iterations=max_iterations,
            members=", ".join(members),
        )

        # Get routing decision from LLM
        try:
            response = llm.invoke(
                [
                    SystemMessage(content=prompt),
                    HumanMessage(content="What is the next agent to route to?"),
                ]
                + messages
            )

            # Parse routing decision
            next_agent = response.content.strip().lower()

            # Validate routing
            if next_agent not in [m.lower() for m in members]:
                logger.warning(
                    "invalid_routing_decision",
                    decision=next_agent,
                    defaulting_to="knowledge",
                )
                next_agent = "knowledge"

            logger.info(
                "supervisor_routing",
                next_agent=next_agent,
                iteration=iteration_count,
                application_id=state.get("application_id"),
            )

            return {
                **state,
                "next_agent": next_agent,
                "current_agent": "supervisor",
                "iteration_count": iteration_count + 1,
            }

        except Exception as e:
            logger.error(
                "supervisor_error",
                error=str(e),
                application_id=state.get("application_id"),
            )
            return {
                **state,
                "next_agent": "FINISH",
                "error": f"Supervisor error: {str(e)}",
                "completed": True,
            }

    return supervisor_node


def route_supervisor(state: AgentState) -> str:
    """Route based on supervisor's decision.

    Args:
        state: Current state

    Returns:
        str: Next node name
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH" or next_agent == "finish":
        return END

    return next_agent


def create_supervisor_graph() -> StateGraph:
    """Create the supervisor orchestration graph.

    Returns:
        StateGraph: Compiled supervisor graph
    """
    # Create graph
    workflow = StateGraph(AgentState)

    # Add supervisor node
    workflow.add_node("supervisor", create_supervisor_node())

    # Add placeholder nodes for specialist agents
    # These will be replaced with actual subgraphs
    from app.graph.agents import (
        create_financing_node,
        create_dealer_matching_node,
        create_knowledge_node,
    )

    workflow.add_node("financing", create_financing_node())
    workflow.add_node("dealer_matching", create_dealer_matching_node())
    workflow.add_node("knowledge", create_knowledge_node())

    # Set entry point
    workflow.set_entry_point("supervisor")

    # Add conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "financing": "financing",
            "dealer_matching": "dealer_matching",
            "knowledge": "knowledge",
            END: END,
        },
    )

    # All specialist agents return to supervisor
    workflow.add_edge("financing", "supervisor")
    workflow.add_edge("dealer_matching", "supervisor")
    workflow.add_edge("knowledge", "supervisor")

    # Compile with checkpointer for persistence
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)

    logger.info("supervisor_graph_created")

    return app
