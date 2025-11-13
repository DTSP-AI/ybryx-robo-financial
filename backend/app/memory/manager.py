"""Memory Manager using Mem0 with namespace isolation and composite scoring."""

from typing import Any, Optional
import structlog
from datetime import datetime, timedelta

from app.config import settings

logger = structlog.get_logger()


class MemoryManager:
    """Mem0-backed memory manager with namespace isolation.

    Implements the Memory Management Standard with:
    - Namespace isolation per agent/tenant
    - Composite scoring (recency + relevance + frequency)
    - TTL and retention policies
    - Async operations
    """

    def __init__(
        self,
        namespace: str,
        retention_days: Optional[int] = None,
        composite_scoring: bool = True,
    ):
        """Initialize memory manager.

        Args:
            namespace: Memory namespace (e.g., "agent:financing", "tenant:uuid")
            retention_days: Days to retain memories (None = forever)
            composite_scoring: Enable composite scoring for retrieval
        """
        self.namespace = namespace
        self.retention_days = retention_days
        self.composite_scoring = composite_scoring

        # Initialize Mem0 client
        try:
            from mem0 import Memory

            self.mem0 = Memory(
                api_key=settings.mem0_api_key,
                host=settings.mem0_host,
            )
            self.enabled = True
            logger.info("mem0_initialized", namespace=namespace)
        except Exception as e:
            logger.warning(
                "mem0_initialization_failed",
                error=str(e),
                namespace=namespace,
            )
            self.enabled = False
            self.mem0 = None

    async def add(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        ttl_hours: Optional[int] = None,
    ) -> Optional[str]:
        """Add a memory.

        Args:
            content: Memory content
            metadata: Additional metadata
            ttl_hours: Time-to-live in hours (overrides retention_days)

        Returns:
            str: Memory ID if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            # Calculate expiration if TTL or retention is set
            expires_at = None
            if ttl_hours:
                expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
            elif self.retention_days:
                expires_at = datetime.utcnow() + timedelta(days=self.retention_days)

            # Merge namespace into metadata
            full_metadata = {
                "namespace": self.namespace,
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {}),
            }

            if expires_at:
                full_metadata["expires_at"] = expires_at.isoformat()

            # Add to Mem0
            result = await self.mem0.add(
                content=content,
                metadata=full_metadata,
            )

            memory_id = result.get("id") if isinstance(result, dict) else str(result)
            logger.info(
                "memory_added",
                memory_id=memory_id,
                namespace=self.namespace,
            )

            return memory_id

        except Exception as e:
            logger.error(
                "memory_add_failed",
                error=str(e),
                namespace=self.namespace,
            )
            return None

    async def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Search memories with composite scoring.

        Args:
            query: Search query
            limit: Maximum results to return
            filters: Additional metadata filters

        Returns:
            list: Matching memories with scores
        """
        if not self.enabled:
            return []

        try:
            # Merge namespace filter
            full_filters = {
                "namespace": self.namespace,
                **(filters or {}),
            }

            # Search Mem0
            results = await self.mem0.search(
                query=query,
                filters=full_filters,
                limit=limit * 2,  # Get more for composite scoring
            )

            # Apply composite scoring if enabled
            if self.composite_scoring:
                scored_results = self._apply_composite_scoring(results)
            else:
                scored_results = results

            # Filter expired memories
            filtered_results = [
                r for r in scored_results
                if not self._is_expired(r.get("metadata", {}))
            ]

            logger.info(
                "memory_search",
                query=query,
                results_count=len(filtered_results),
                namespace=self.namespace,
            )

            return filtered_results[:limit]

        except Exception as e:
            logger.error(
                "memory_search_failed",
                error=str(e),
                namespace=self.namespace,
            )
            return []

    async def get(self, memory_id: str) -> Optional[dict[str, Any]]:
        """Get specific memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            dict: Memory data or None
        """
        if not self.enabled:
            return None

        try:
            result = await self.mem0.get(memory_id)

            # Check if expired
            if self._is_expired(result.get("metadata", {})):
                await self.delete(memory_id)
                return None

            return result

        except Exception as e:
            logger.error(
                "memory_get_failed",
                error=str(e),
                memory_id=memory_id,
            )
            return None

    async def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Update existing memory.

        Args:
            memory_id: Memory identifier
            content: New content (None = keep existing)
            metadata: Metadata to merge (None = keep existing)

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        try:
            update_data = {}
            if content:
                update_data["content"] = content
            if metadata:
                update_data["metadata"] = metadata

            await self.mem0.update(memory_id, **update_data)

            logger.info(
                "memory_updated",
                memory_id=memory_id,
                namespace=self.namespace,
            )
            return True

        except Exception as e:
            logger.error(
                "memory_update_failed",
                error=str(e),
                memory_id=memory_id,
            )
            return False

    async def delete(self, memory_id: str) -> bool:
        """Delete memory.

        Args:
            memory_id: Memory identifier

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        try:
            await self.mem0.delete(memory_id)

            logger.info(
                "memory_deleted",
                memory_id=memory_id,
                namespace=self.namespace,
            )
            return True

        except Exception as e:
            logger.error(
                "memory_delete_failed",
                error=str(e),
                memory_id=memory_id,
            )
            return False

    async def clear_namespace(self) -> bool:
        """Clear all memories in this namespace.

        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False

        try:
            # Search all in namespace and delete
            results = await self.mem0.search(
                query="",
                filters={"namespace": self.namespace},
                limit=1000,
            )

            for result in results:
                await self.delete(result["id"])

            logger.info(
                "namespace_cleared",
                namespace=self.namespace,
                count=len(results),
            )
            return True

        except Exception as e:
            logger.error(
                "namespace_clear_failed",
                error=str(e),
                namespace=self.namespace,
            )
            return False

    def _apply_composite_scoring(
        self,
        results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Apply composite scoring: recency + relevance + frequency.

        Args:
            results: Search results from Mem0

        Returns:
            list: Results sorted by composite score
        """
        scored = []
        now = datetime.utcnow()

        for result in results:
            relevance_score = result.get("score", 0.5)
            metadata = result.get("metadata", {})

            # Recency score (decay over time)
            created_at_str = metadata.get("created_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                age_days = (now - created_at).days
                recency_score = max(0, 1 - (age_days / 30))  # Decay over 30 days
            else:
                recency_score = 0.5

            # Frequency score (access count)
            access_count = metadata.get("access_count", 0)
            frequency_score = min(1.0, access_count / 10)  # Max at 10 accesses

            # Composite score (weighted average)
            composite_score = (
                0.5 * relevance_score +
                0.3 * recency_score +
                0.2 * frequency_score
            )

            result["composite_score"] = composite_score
            scored.append(result)

        # Sort by composite score
        scored.sort(key=lambda x: x["composite_score"], reverse=True)
        return scored

    def _is_expired(self, metadata: dict[str, Any]) -> bool:
        """Check if memory has expired.

        Args:
            metadata: Memory metadata

        Returns:
            bool: True if expired
        """
        expires_at_str = metadata.get("expires_at")
        if not expires_at_str:
            return False

        try:
            expires_at = datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
            return datetime.utcnow() > expires_at
        except Exception:
            return False
