"""
Memory Writer Node for LangGraph

Writes agent execution results to persistent memory.
Integrates with unified MemoryManager.

Follows AGENT_ORCHESTRATION_STANDARD.md and AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md
"""

from typing import Any, Dict, List
import structlog
from datetime import datetime
from uuid import uuid4

from app.graph.state import AgentState
from app.memory.unified_manager import get_memory_manager

logger = structlog.get_logger()


async def memory_writer_node(state: AgentState) -> AgentState:
    """
    Write agent execution results to memory.

    This node:
    1. Extracts key information from agent execution
    2. Constructs JSONContract-compliant payload
    3. Calls MemoryManager.write_memory()
    4. Logs execution to Supabase audit

    Args:
        state: Current agent state with execution results

    Returns:
        AgentState: Updated state with write confirmation
    """
    logger.info(
        "memory_writer_node_invoked",
        user_id=state.get("user_id"),
        session_id=state.get("application_id"),
        current_agent=state.get("current_agent"),
    )

    user_id = state.get("user_id")
    session_id = state.get("application_id")
    agent_name = state.get("current_agent", "unknown")
    messages = state.get("messages", [])

    if not user_id or not session_id:
        logger.warning(
            "memory_write_skipped",
            reason="missing user_id or session_id",
        )
        return state

    try:
        memory_manager = get_memory_manager()

        # Extract last message or execution summary
        if messages:
            last_message = messages[-1]
            content_summary = {
                "role": last_message.get("role", "assistant"),
                "content": last_message.get("content", ""),
                "tool_calls": last_message.get("tool_calls", []),
                "execution_summary": {
                    "iteration_count": state.get("iteration_count", 0),
                    "completed": state.get("completed", False),
                    "error": state.get("error"),
                },
            }
        else:
            content_summary = {
                "execution_summary": "No messages in state",
            }

        # Construct JSONContract-compliant payload
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent": agent_name,
            "session_id": session_id,
            "type": "agent_execution_result",
            "content": content_summary,
        }

        # Determine memory type based on agent
        memory_type = "long_term"  # Default
        if agent_name == "financing":
            memory_type = "episodic"  # Specific financing episodes
        elif agent_name == "knowledge":
            memory_type = "semantic"  # Factual knowledge

        # Extract tags from state
        tags = []
        if state.get("industry"):
            tags.append(state["industry"])
        if state.get("application_data"):
            tags.append("prequalification")
        tags.append(agent_name)

        # Write to memory
        write_result = await memory_manager.write_memory(
            user_id=user_id,
            session_id=session_id,
            payload=payload,
            memory_type=memory_type,
            tags=tags,
        )

        # Log agent execution to Supabase
        if state.get("completed"):
            await memory_manager.log_agent_execution(
                user_id=user_id,
                session_id=session_id,
                agent_name=agent_name,
                execution_id=str(uuid4()),
                input_payload={"messages": messages[:1] if messages else []},
                output_payload={"messages": messages[-1:] if messages else []},
                status="completed" if not state.get("error") else "failed",
                error_details={"error": state.get("error")} if state.get("error") else None,
            )

        logger.info(
            "memory_written",
            user_id=user_id,
            supabase_id=write_result.get("supabase_id"),
            mem0_id=write_result.get("mem0_id"),
            memory_type=memory_type,
        )

        # Update state with write confirmation
        return {
            **state,
            "memory_written": True,
            "memory_write_result": write_result,
        }

    except Exception as e:
        logger.error(
            "memory_write_failed",
            error=str(e),
            user_id=user_id,
            session_id=session_id,
            exc_info=True,
        )

        return {
            **state,
            "memory_write_error": str(e),
        }


# Sync wrapper for LangGraph compatibility
def memory_writer_node_sync(state: AgentState) -> AgentState:
    """
    Synchronous wrapper for memory_writer_node.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(memory_writer_node(state))
