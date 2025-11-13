"""
Context Loader Node for LangGraph

Loads contextual memory snapshot at the start of agent execution.
Integrates with unified MemoryManager.

Follows AGENT_ORCHESTRATION_STANDARD.md
"""

from typing import Any, Dict
import structlog
from datetime import datetime

from app.graph.state import AgentState
from app.memory.unified_manager import get_memory_manager

logger = structlog.get_logger()


async def context_loader_node(state: AgentState) -> AgentState:
    """
    Load contextual memory for agent execution.

    This node:
    1. Retrieves user_id and session_id from state
    2. Calls MemoryManager.load_context()
    3. Populates state with:
       - Recent memories
       - Active goals
       - Belief graph
       - Session metadata

    Args:
        state: Current agent state

    Returns:
        AgentState: Updated state with memory context
    """
    logger.info(
        "context_loader_node_invoked",
        user_id=state.get("user_id"),
        session_id=state.get("application_id"),
    )

    user_id = state.get("user_id")
    session_id = state.get("application_id")  # Using application_id as session_id
    agent_name = state.get("current_agent", "supervisor")

    if not user_id or not session_id:
        logger.warning(
            "context_load_skipped",
            reason="missing user_id or session_id",
        )
        return state

    try:
        # Get memory manager instance
        memory_manager = get_memory_manager()

        # Load full context
        context = await memory_manager.load_context(
            user_id=user_id,
            session_id=session_id,
            agent_name=agent_name,
            include_goals=True,
            include_beliefs=True,
            max_memories=10,
        )

        # Update state with loaded context
        updated_state = {
            **state,
            "memory_context": context.get("recent_memories", []),
            "goals": context.get("goals", []),
            "beliefs": context.get("beliefs", []),
            "session_metadata": context.get("session"),
            "context_loaded_at": datetime.utcnow().isoformat(),
        }

        logger.info(
            "context_loaded",
            user_id=user_id,
            memories_loaded=len(context.get("recent_memories", [])),
            goals_loaded=len(context.get("goals", [])),
            beliefs_loaded=len(context.get("beliefs", [])),
        )

        return updated_state

    except Exception as e:
        logger.error(
            "context_load_failed",
            error=str(e),
            user_id=user_id,
            session_id=session_id,
            exc_info=True,
        )

        # Return state with error flag
        return {
            **state,
            "error": f"Context load failed: {str(e)}",
            "memory_context": [],
        }


# Sync wrapper for LangGraph compatibility (if needed)
def context_loader_node_sync(state: AgentState) -> AgentState:
    """
    Synchronous wrapper for context_loader_node.

    Some LangGraph versions may require sync nodes.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(context_loader_node(state))
