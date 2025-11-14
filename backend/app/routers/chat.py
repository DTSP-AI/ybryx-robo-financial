"""Chat API endpoints for sales agent interactions."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import structlog
import uuid
from datetime import datetime

from langchain_core.messages import HumanMessage, AIMessage

from app.graph.agents import create_sales_agent_node
from app.graph.state import AgentState

logger = structlog.get_logger()

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatMessage(BaseModel):
    """Single chat message."""

    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request from user."""

    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default_factory=list,
        description="Previous messages in conversation"
    )


class ChatResponse(BaseModel):
    """Chat response from sales agent."""

    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


# In-memory session storage (use Supabase for production persistence)
chat_sessions = {}


@router.post("/", response_model=ChatResponse)
async def chat_with_sales_agent(request: ChatRequest):
    """Chat with the sales agent (Alex).

    This endpoint handles conversations with the Level 1 Sales Agent
    on the landing page. The agent helps prospects:
    - Navigate the site
    - Learn about equipment and leasing
    - Start the prequalification process

    Args:
        request: Chat request with message and optional session

    Returns:
        ChatResponse with agent's reply
    """
    try:
        # Generate or retrieve session ID
        session_id = request.session_id or str(uuid.uuid4())

        logger.info(
            "chat_request_received",
            session_id=session_id,
            message_length=len(request.message),
            has_history=bool(request.conversation_history),
        )

        # Build conversation history
        messages = []
        if request.conversation_history:
            for msg in request.conversation_history:
                if msg.role == "user":
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == "assistant":
                    messages.append(AIMessage(content=msg.content))

        # Add current message
        messages.append(HumanMessage(content=request.message))

        # Create initial state
        state: AgentState = {
            "messages": messages,
            "session_id": session_id,
            "current_agent": None,
            "next_agent": None,
            "metadata": {
                "source": "landing_page_chat",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        # Invoke sales agent
        sales_agent = create_sales_agent_node()
        result_state = sales_agent(state)

        # Check for errors
        if "error" in result_state:
            logger.error(
                "chat_agent_error",
                session_id=session_id,
                error=result_state["error"],
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Agent processing error",
            )

        # Extract agent response
        agent_messages = result_state.get("messages", [])
        if not agent_messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No response from agent",
            )

        # Get last message (agent's response)
        last_message = agent_messages[-1]
        agent_response = last_message.content if hasattr(last_message, 'content') else str(last_message)

        # Store session (in production, use Supabase for persistence)
        chat_sessions[session_id] = {
            "messages": agent_messages,
            "last_activity": datetime.utcnow(),
        }

        logger.info(
            "chat_response_sent",
            session_id=session_id,
            response_length=len(agent_response),
        )

        return ChatResponse(
            success=True,
            data={
                "message": agent_response,
                "session_id": session_id,
                "agent": "Alex",
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "chat_endpoint_error",
            error=str(e),
            exc_info=True,
        )
        return ChatResponse(
            success=False,
            error="Failed to process chat message",
        )


@router.get("/health")
async def chat_health():
    """Health check for chat endpoint."""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "agent": "sales",
            "model": "gpt-5-nano",
            "active_sessions": len(chat_sessions),
        },
    }


@router.delete("/session/{session_id}")
async def end_chat_session(session_id: str):
    """End a chat session and clear history.

    Args:
        session_id: Session to end

    Returns:
        Success response
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]
        logger.info("chat_session_ended", session_id=session_id)

    return {
        "success": True,
        "data": {"message": "Session ended"},
    }
