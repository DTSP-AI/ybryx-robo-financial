"""
Unified Memory Manager for Ybryx Capital Agent System

This module serves as the SOLE authority for all memory operations,
coordinating both Supabase (relational) and Mem0 (vector) storage.

Follows:
- MEMORY_MANAGEMENT_STANDARD.md
- AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md
- AGENT_CREATION_STANDARD.md (retry patterns)
- AGENT_ORCHESTRATION_STANDARD.md

NO OTHER FILES SHOULD DIRECTLY ACCESS SUPABASE OR MEM0 CLIENTS.
"""

import os
import asyncio
from typing import Any, Optional, List, Dict
from datetime import datetime, timedelta
from functools import wraps
import structlog
from uuid import uuid4

# Supabase
from supabase import create_client, Client as SupabaseClient

# Mem0
try:
    from mem0 import MemoryClient
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    MemoryClient = None

# OpenAI for embeddings
from openai import AsyncOpenAI

# Retry decorator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = structlog.get_logger()


# ============================================================================
# EXCEPTIONS
# ============================================================================

class MemoryManagerError(Exception):
    """Base exception for memory manager errors."""
    pass


class SupabaseConnectionError(MemoryManagerError):
    """Supabase connection or query error."""
    pass


class Mem0ConnectionError(MemoryManagerError):
    """Mem0 connection or operation error."""
    pass


class JSONContractViolation(MemoryManagerError):
    """Payload does not conform to JSONContract standard."""
    pass


# ============================================================================
# RETRY DECORATORS (AGENT_CREATION_STANDARD.md)
# ============================================================================

def retry_on_failure(max_attempts: int = 3):
    """Retry decorator for resilient operations."""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
        reraise=True,
    )


# ============================================================================
# JSONCONTRACT VALIDATOR
# ============================================================================

def validate_jsoncontract(payload: Dict[str, Any]) -> None:
    """
    Validates that a payload conforms to JSONContract standard.

    Required fields:
    - timestamp: ISO8601 string
    - agent: agent name/identifier
    - session_id: session identifier
    - type: event/action type
    - content: dict with actual data

    Raises:
        JSONContractViolation: If payload is invalid
    """
    required_fields = ["timestamp", "agent", "session_id", "type", "content"]

    for field in required_fields:
        if field not in payload:
            raise JSONContractViolation(f"Missing required field: {field}")

    # Validate timestamp format
    try:
        datetime.fromisoformat(payload["timestamp"].replace("Z", "+00:00"))
    except (ValueError, AttributeError) as e:
        raise JSONContractViolation(f"Invalid timestamp format: {e}")

    # Validate content is dict
    if not isinstance(payload["content"], dict):
        raise JSONContractViolation("'content' must be a dictionary")


# ============================================================================
# UNIFIED MEMORY MANAGER
# ============================================================================

class MemoryManager:
    """
    Unified controller for all memory operations in the Ybryx agent system.

    Coordinates:
    - Supabase: Structured, relational, transactional data
    - Mem0: Vector embeddings, semantic search, context recall
    - OpenAI: Embedding generation

    All agent memory operations MUST flow through this class.
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        mem0_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-large",
        embedding_dimensions: int = 1536,
    ):
        """
        Initialize the unified memory manager.

        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service role key
            mem0_api_key: Mem0 API key
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model
            embedding_dimensions: Embedding vector dimensions
        """
        # Load from environment if not provided
        # Accept both SUPABASE_SERVICE_KEY and SUPABASE_SERVICE_ROLE_KEY for compatibility
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        self.mem0_api_key = mem0_api_key or os.getenv("MEM0_API_KEY")
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        self.embedding_model = embedding_model
        self.embedding_dimensions = embedding_dimensions

        # Initialize clients
        self._init_supabase()
        self._init_mem0()
        self._init_embedder()

        logger.info(
            "memory_manager_initialized",
            supabase_connected=self.supabase is not None,
            mem0_connected=self.mem0 is not None,
            embedder_configured=self.embedder is not None,
        )

    def _init_supabase(self) -> None:
        """Initialize Supabase client with startup validation."""
        if not self.supabase_url or not self.supabase_key:
            logger.warning(
                "supabase_not_configured",
                message="SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/SUPABASE_SERVICE_KEY not set",
                has_url=bool(self.supabase_url),
                has_key=bool(self.supabase_key),
            )
            self.supabase: Optional[SupabaseClient] = None
            return

        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)

            # Startup validation: Test connection by querying sessions table
            try:
                test_query = self.supabase.table("sessions").select("id").limit(1).execute()
                logger.info(
                    "supabase_client_initialized",
                    connection_validated=True,
                    url=self.supabase_url[:30] + "..."
                )
            except Exception as test_error:
                logger.warning(
                    "supabase_validation_failed",
                    error=str(test_error),
                    message="Supabase client created but test query failed - check schema/permissions"
                )

        except Exception as e:
            logger.error("supabase_initialization_failed", error=str(e), exc_info=True)
            self.supabase = None
            raise SupabaseConnectionError(f"Failed to initialize Supabase: {e}")

    def _init_mem0(self) -> None:
        """Initialize Mem0 client."""
        if not MEM0_AVAILABLE:
            logger.warning("mem0_not_installed", message="mem0 package not available")
            self.mem0 = None
            return

        if not self.mem0_api_key:
            logger.warning("mem0_not_configured", message="MEM0_API_KEY not set")
            self.mem0 = None
            return

        try:
            self.mem0 = MemoryClient(api_key=self.mem0_api_key)
            logger.info("mem0_client_initialized")
        except Exception as e:
            logger.error("mem0_initialization_failed", error=str(e), exc_info=True)
            self.mem0 = None
            # Don't raise - Mem0 is optional if fallback is available

    def _init_embedder(self) -> None:
        """Initialize OpenAI embedder."""
        if not self.openai_api_key:
            logger.warning("openai_not_configured", message="OPENAI_API_KEY not set")
            self.embedder = None
            return

        try:
            self.embedder = AsyncOpenAI(api_key=self.openai_api_key)
            logger.info("openai_embedder_initialized", model=self.embedding_model)
        except Exception as e:
            logger.error("embedder_initialization_failed", error=str(e), exc_info=True)
            self.embedder = None

    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not self.embedder:
            logger.warning("embedder_not_available")
            return None

        try:
            response = await self.embedder.embeddings.create(
                model=self.embedding_model,
                input=text,
                dimensions=self.embedding_dimensions,
            )
            embedding = response.data[0].embedding
            logger.debug("embedding_generated", text_length=len(text))
            return embedding
        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e), exc_info=True)
            return None

    # ========================================================================
    # SESSION MANAGEMENT HELPERS
    # ========================================================================

    async def resolve_session_uuid(
        self,
        session_id: str,
        user_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Resolve a session_id string to its Supabase UUID primary key.

        Creates the session if it doesn't exist. This ensures foreign key
        constraints are satisfied when writing to memory_logs.

        Args:
            session_id: External session identifier (string)
            user_id: Optional user ID (can be null)
            agent_name: Optional agent name

        Returns:
            UUID string from sessions.id, or None if Supabase unavailable
        """
        if not self.supabase:
            logger.debug("session_resolution_skipped_no_supabase")
            return None

        try:
            # Try to find existing session
            response = self.supabase.table("sessions").select("id").eq("session_id", session_id).limit(1).execute()

            if response.data and len(response.data) > 0:
                uuid = response.data[0]["id"]
                logger.debug("session_uuid_resolved", session_id=session_id, uuid=uuid)
                return uuid

            # Session doesn't exist - create it
            session_data = {
                "session_id": session_id,
                "user_id": user_id,  # Nullable FK
                "agent_name": agent_name or "unknown",
                "status": "active",
            }

            create_response = self.supabase.table("sessions").insert(session_data).execute()

            if create_response.data and len(create_response.data) > 0:
                uuid = create_response.data[0]["id"]
                logger.info("session_created", session_id=session_id, uuid=uuid, user_id=user_id)
                return uuid

            logger.warning("session_creation_failed_no_data", session_id=session_id)
            return None

        except Exception as e:
            logger.error("session_resolution_failed", error=str(e), session_id=session_id, exc_info=True)
            return None

    # ========================================================================
    # CORE METHODS
    # ========================================================================

    @retry_on_failure(max_attempts=3)
    async def load_context(
        self,
        user_id: str,
        session_id: str,
        agent_name: Optional[str] = None,
        include_goals: bool = True,
        include_beliefs: bool = True,
        max_memories: int = 10,
    ) -> Dict[str, Any]:
        """
        Load contextual snapshot for an agent's runtime.

        Retrieves:
        - Session metadata from Supabase
        - Recent memory vectors from Mem0
        - Active goals (if requested)
        - Belief graph (if requested)

        Args:
            user_id: User identifier
            session_id: Session identifier
            agent_name: Optional agent filter
            include_goals: Include goal assessments
            include_beliefs: Include belief graph
            max_memories: Maximum recent memories to retrieve

        Returns:
            dict: Contextual snapshot with all relevant data
        """
        logger.info(
            "loading_context",
            user_id=user_id,
            session_id=session_id,
            agent_name=agent_name,
        )

        context = {
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "loaded_at": datetime.utcnow().isoformat(),
            "session": None,
            "recent_memories": [],
            "goals": [],
            "beliefs": [],
        }

        try:
            # 1. Load session from Supabase
            if self.supabase:
                session_response = self.supabase.table("sessions").select("*").eq("session_id", session_id).execute()
                if session_response.data:
                    context["session"] = session_response.data[0]

            # 2. Load recent memories from Mem0
            if self.mem0:
                try:
                    # Query Mem0 for recent memories
                    mem0_filters = {
                        "user_id": user_id,
                        "session_id": session_id,
                    }
                    if agent_name:
                        mem0_filters["agent_name"] = agent_name

                    memories = self.mem0.search(
                        query="",  # Empty query for recent items
                        user_id=user_id,
                        filters=mem0_filters,
                        limit=max_memories,
                    )
                    context["recent_memories"] = memories if memories else []
                except Exception as e:
                    logger.error("mem0_load_failed", error=str(e))

            # 3. Load goals if requested
            if include_goals and self.supabase:
                goals_response = self.supabase.table("goal_assessments").select("*").eq("user_id", user_id).eq("session_id", session_id).eq("status", "active").execute()
                context["goals"] = goals_response.data if goals_response.data else []

            # 4. Load beliefs if requested
            if include_beliefs and self.supabase:
                beliefs_response = self.supabase.table("belief_graphs").select("*").eq("user_id", user_id).eq("session_id", session_id).execute()
                context["beliefs"] = beliefs_response.data if beliefs_response.data else []

            # Log context load to audit
            await self.log_event(
                user_id=user_id,
                event_type="context_loaded",
                data={
                    "session_id": session_id,
                    "agent_name": agent_name,
                    "memory_count": len(context["recent_memories"]),
                    "goal_count": len(context["goals"]),
                    "belief_count": len(context["beliefs"]),
                },
            )

            logger.info(
                "context_loaded",
                user_id=user_id,
                session_id=session_id,
                memories=len(context["recent_memories"]),
                goals=len(context["goals"]),
                beliefs=len(context["beliefs"]),
            )

            return context

        except Exception as e:
            logger.error("context_load_failed", error=str(e), exc_info=True)
            await self.log_event(
                user_id=user_id,
                event_type="context_load_error",
                data={"error": str(e), "session_id": session_id},
            )
            raise MemoryManagerError(f"Failed to load context: {e}")

    @retry_on_failure(max_attempts=3)
    async def write_memory(
        self,
        user_id: str,
        session_id: str,
        payload: Dict[str, Any],
        memory_type: str = "long_term",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Write new memory to both Supabase (structured) and Mem0 (vector).

        Enforces JSONContract compliance.

        Args:
            user_id: User identifier
            session_id: Session identifier
            payload: JSONContract-compliant payload
            memory_type: Type of memory (short_term, long_term, episodic, semantic, procedural)
            tags: Optional tags for categorization

        Returns:
            dict: Write confirmation with IDs

        Raises:
            JSONContractViolation: If payload doesn't meet standards
        """
        logger.info(
            "writing_memory",
            user_id=user_id,
            session_id=session_id,
            memory_type=memory_type,
        )

        # Validate JSONContract
        validate_jsoncontract(payload)

        result = {
            "user_id": user_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "supabase_id": None,
            "mem0_id": None,
            "written_at": datetime.utcnow().isoformat(),
        }

        try:
            content_text = str(payload.get("content", ""))
            agent_name = payload.get("agent", "unknown")

            # 0. Resolve session UUID for FK constraint
            session_uuid = await self.resolve_session_uuid(
                session_id=session_id,
                user_id=user_id,
                agent_name=agent_name
            )

            # 1. Write to Mem0 (vector) FIRST to get vector_id
            if self.mem0:
                try:
                    mem0_metadata = {
                        "user_id": user_id,
                        "session_id": session_id,
                        "agent_name": agent_name,
                        "memory_type": memory_type,
                        "tags": tags or [],
                        "timestamp": payload.get("timestamp"),
                    }

                    mem0_response = self.mem0.add(
                        messages=[{"role": "user", "content": content_text}],
                        user_id=user_id,
                        metadata=mem0_metadata,
                    )

                    # Mem0 returns different response formats depending on version
                    if isinstance(mem0_response, dict):
                        result["mem0_id"] = mem0_response.get("id")
                    elif isinstance(mem0_response, list) and len(mem0_response) > 0:
                        result["mem0_id"] = mem0_response[0].get("id")

                except Exception as e:
                    logger.error("mem0_write_failed", error=str(e))

            # 2. Write to Supabase (structured log) with vector_id
            if self.supabase and session_uuid:
                memory_log = {
                    "user_id": user_id,
                    "session_id": session_uuid,  # Use resolved UUID for FK constraint
                    "agent_name": agent_name,
                    "operation_type": "write",
                    "memory_type": memory_type,
                    "content": content_text,
                    "tags": tags or [],
                    "metadata": payload,
                    "vector_id": result.get("mem0_id"),  # Link to Mem0 vector for recall
                }

                supabase_response = self.supabase.table("memory_logs").insert(memory_log).execute()
                if supabase_response.data:
                    result["supabase_id"] = supabase_response.data[0].get("id")

            # 3. Audit log
            await self.log_event(
                user_id=user_id,
                event_type="memory_written",
                data={
                    "session_id": session_id,
                    "memory_type": memory_type,
                    "agent_name": agent_name,
                    "supabase_id": result["supabase_id"],
                    "mem0_id": result["mem0_id"],
                },
            )

            logger.info(
                "memory_written",
                user_id=user_id,
                supabase_id=result["supabase_id"],
                mem0_id=result["mem0_id"],
            )

            return result

        except JSONContractViolation:
            raise
        except Exception as e:
            logger.error("memory_write_failed", error=str(e), exc_info=True)
            await self.log_event(
                user_id=user_id,
                event_type="memory_write_error",
                data={"error": str(e), "session_id": session_id},
            )
            raise MemoryManagerError(f"Failed to write memory: {e}")

    @retry_on_failure(max_attempts=3)
    async def recall_memory(
        self,
        user_id: str,
        query: str,
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity recall from Mem0 with optional Supabase enrichment.

        Args:
            user_id: User identifier
            query: Search query for semantic similarity
            session_id: Optional session filter
            agent_name: Optional agent filter
            tags: Optional tag filters
            limit: Maximum results

        Returns:
            list: Matching memories with metadata
        """
        logger.info(
            "recalling_memory",
            user_id=user_id,
            query=query[:50],
            session_id=session_id,
        )

        if not self.mem0:
            logger.warning("mem0_not_available_for_recall")
            return []

        try:
            # Build Mem0 filters
            filters = {"user_id": user_id}
            if session_id:
                filters["session_id"] = session_id
            if agent_name:
                filters["agent_name"] = agent_name
            if tags:
                filters["tags"] = tags

            # Query Mem0
            memories = self.mem0.search(
                query=query,
                user_id=user_id,
                filters=filters,
                limit=limit,
            )

            # Enrich with Supabase data if available
            enriched_memories = []
            if self.supabase and memories:
                for memory in memories:
                    # Try to fetch corresponding Supabase log
                    mem0_id = memory.get("id")
                    if mem0_id:
                        supabase_log = self.supabase.table("memory_logs").select("*").eq("vector_id", mem0_id).limit(1).execute()
                        if supabase_log.data:
                            memory["supabase_data"] = supabase_log.data[0]

                    enriched_memories.append(memory)
            else:
                enriched_memories = memories if memories else []

            # Log recall operation
            await self.log_event(
                user_id=user_id,
                event_type="memory_recalled",
                data={
                    "query": query[:100],
                    "session_id": session_id,
                    "agent_name": agent_name,
                    "results_count": len(enriched_memories),
                },
            )

            logger.info(
                "memory_recalled",
                user_id=user_id,
                results_count=len(enriched_memories),
            )

            return enriched_memories

        except Exception as e:
            logger.error("memory_recall_failed", error=str(e), exc_info=True)
            await self.log_event(
                user_id=user_id,
                event_type="memory_recall_error",
                data={"error": str(e), "query": query[:100]},
            )
            return []

    async def log_event(
        self,
        user_id: str,
        event_type: str,
        data: Dict[str, Any],
        event_category: str = "memory",
        severity: str = "info",
        session_id: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> None:
        """
        Write event to Supabase audit_logs.

        Args:
            user_id: User identifier
            event_type: Type of event
            data: Event data
            event_category: Category (memory, agent, security, etc.)
            severity: Severity level
            session_id: Optional session ID (will be resolved to UUID if provided)
            agent_name: Optional agent name
        """
        if not self.supabase:
            logger.debug("audit_log_skipped_no_supabase", event_type=event_type)
            return

        try:
            # Resolve session UUID if session_id provided
            session_uuid = None
            if session_id:
                session_uuid = await self.resolve_session_uuid(
                    session_id=session_id,
                    user_id=user_id,
                    agent_name=agent_name
                )

            audit_entry = {
                "user_id": user_id,
                "session_id": session_uuid,  # Use resolved UUID for FK constraint
                "agent_name": agent_name,
                "event_type": event_type,
                "event_category": event_category,
                "severity": severity,
                "message": f"{event_type}: {data.get('message', '')}",
                "data": data,
            }

            self.supabase.table("audit_logs").insert(audit_entry).execute()

            logger.debug("audit_log_written", event_type=event_type)

        except Exception as e:
            logger.error("audit_log_failed", error=str(e), event_type=event_type)

    @retry_on_failure(max_attempts=3)
    async def decay_memory(
        self,
        user_id: str,
        threshold_days: int = 30,
        memory_type: Optional[str] = None,
    ) -> Dict[str, int]:
        """
        Trim or decay vector memory beyond retention window.

        Args:
            user_id: User identifier
            threshold_days: Days beyond which to decay
            memory_type: Optional type filter

        Returns:
            dict: Counts of decayed memories
        """
        logger.info(
            "decaying_memory",
            user_id=user_id,
            threshold_days=threshold_days,
            memory_type=memory_type,
        )

        result = {
            "supabase_deleted": 0,
            "mem0_deleted": 0,
        }

        try:
            cutoff_date = datetime.utcnow() - timedelta(days=threshold_days)

            # 1. Delete from Supabase
            if self.supabase:
                query = self.supabase.table("memory_logs").delete().eq("user_id", user_id).lt("timestamp", cutoff_date.isoformat())

                if memory_type:
                    query = query.eq("memory_type", memory_type)

                response = query.execute()
                result["supabase_deleted"] = len(response.data) if response.data else 0

            # 2. Delete from Mem0 (if supported)
            if self.mem0:
                try:
                    # Mem0 may have a delete_all or similar method
                    # This is placeholder - check Mem0 SDK for actual method
                    filters = {
                        "user_id": user_id,
                        "created_before": cutoff_date.isoformat(),
                    }
                    if memory_type:
                        filters["memory_type"] = memory_type

                    # mem0_response = self.mem0.delete_many(filters=filters)
                    # result["mem0_deleted"] = mem0_response.get("deleted_count", 0)

                except Exception as e:
                    logger.error("mem0_decay_failed", error=str(e))

            # Log decay operation
            await self.log_event(
                user_id=user_id,
                event_type="memory_decayed",
                data={
                    "threshold_days": threshold_days,
                    "memory_type": memory_type,
                    "supabase_deleted": result["supabase_deleted"],
                    "mem0_deleted": result["mem0_deleted"],
                },
            )

            logger.info(
                "memory_decayed",
                user_id=user_id,
                supabase_deleted=result["supabase_deleted"],
                mem0_deleted=result["mem0_deleted"],
            )

            return result

        except Exception as e:
            logger.error("memory_decay_failed", error=str(e), exc_info=True)
            await self.log_event(
                user_id=user_id,
                event_type="memory_decay_error",
                data={"error": str(e)},
            )
            raise MemoryManagerError(f"Failed to decay memory: {e}")

    # ========================================================================
    # ADDITIONAL HELPER METHODS
    # ========================================================================

    async def create_session(
        self,
        user_id: str,
        agent_name: str,
        client_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new session in Supabase.

        Args:
            user_id: User identifier
            agent_name: Agent name
            client_info: Optional client metadata

        Returns:
            str: Session ID
        """
        if not self.supabase:
            raise SupabaseConnectionError("Supabase not configured")

        session_id = str(uuid4())

        session_data = {
            "user_id": user_id,
            "session_id": session_id,
            "agent_name": agent_name,
            "client_info": client_info or {},
            "status": "active",
        }

        response = self.supabase.table("sessions").insert(session_data).execute()

        logger.info("session_created", session_id=session_id, user_id=user_id)

        return session_id

    async def close_session(
        self,
        session_id: str,
        status: str = "completed",
    ) -> None:
        """
        Close an active session.

        Args:
            session_id: Session identifier
            status: Final status (completed, failed, timeout)
        """
        if not self.supabase:
            return

        self.supabase.table("sessions").update({
            "status": status,
            "ended_at": datetime.utcnow().isoformat(),
        }).eq("session_id", session_id).execute()

        logger.info("session_closed", session_id=session_id, status=status)

    async def log_agent_execution(
        self,
        user_id: str,
        session_id: str,
        agent_name: str,
        execution_id: str,
        input_payload: Dict[str, Any],
        output_payload: Optional[Dict[str, Any]] = None,
        status: str = "running",
        error_details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Log agent execution to Supabase.

        Args:
            user_id: User identifier
            session_id: Session identifier (will be resolved to UUID)
            agent_name: Agent name
            execution_id: Unique execution ID
            input_payload: Input data
            output_payload: Output data (if completed)
            status: Execution status
            error_details: Error information if failed

        Returns:
            str: Execution record ID
        """
        if not self.supabase:
            return ""

        # Resolve session UUID for FK constraint
        session_uuid = await self.resolve_session_uuid(
            session_id=session_id,
            user_id=user_id,
            agent_name=agent_name
        )

        execution_data = {
            "user_id": user_id,
            "session_id": session_uuid,  # Use resolved UUID for FK constraint
            "agent_name": agent_name,
            "execution_id": execution_id,
            "input_payload": input_payload,
            "output_payload": output_payload,
            "status": status,
            "error_details": error_details,
        }

        response = self.supabase.table("agent_executions").insert(execution_data).execute()

        exec_id = response.data[0].get("id") if response.data else ""

        logger.info(
            "agent_execution_logged",
            execution_id=execution_id,
            status=status,
        )

        return exec_id


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

# Global instance (initialized on first import)
_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """
    Get or create the global MemoryManager instance.

    Returns:
        MemoryManager: Singleton instance
    """
    global _memory_manager_instance

    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()

    return _memory_manager_instance
