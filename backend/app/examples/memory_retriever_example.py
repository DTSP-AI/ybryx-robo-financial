"""
Example: Using MemoryManager as a LangChain Retriever

Demonstrates integration of unified memory system with LangChain's
retriever interface for use in agent chains and RAG patterns.
"""

from typing import List, Any, Dict
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
import structlog

from app.memory.unified_manager import get_memory_manager

logger = structlog.get_logger()


class MemoryRetriever(BaseRetriever):
    """
    LangChain-compatible retriever using unified MemoryManager.

    Wraps MemoryManager.recall_memory() to provide standard
    retriever interface for use in chains.
    """

    user_id: str
    session_id: str
    agent_name: str = "retriever"
    k: int = 5  # Default number of results

    class Config:
        """Pydantic config."""
        arbitrary_types_allowed = True

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun = None,
    ) -> List[Document]:
        """
        Retrieve relevant documents based on query.

        Args:
            query: Search query
            run_manager: Callback manager (optional)

        Returns:
            List[Document]: Retrieved documents
        """
        logger.info(
            "memory_retriever_invoked",
            user_id=self.user_id,
            session_id=self.session_id,
            query=query[:50],
        )

        try:
            # Get memory manager
            memory_manager = get_memory_manager()

            # Recall memories
            import asyncio
            memories = asyncio.run(
                memory_manager.recall_memory(
                    user_id=self.user_id,
                    query=query,
                    session_id=self.session_id,
                    agent_name=self.agent_name,
                    limit=self.k,
                )
            )

            # Convert to LangChain Documents
            documents = []
            for memory in memories:
                # Extract content
                content = memory.get("content", "")
                if isinstance(content, dict):
                    content = str(content)

                # Extract metadata
                metadata = {
                    "memory_id": memory.get("id"),
                    "score": memory.get("score", 0.0),
                    "user_id": memory.get("user_id", self.user_id),
                    "session_id": memory.get("session_id", self.session_id),
                    "agent_name": memory.get("agent_name", self.agent_name),
                    "tags": memory.get("metadata", {}).get("tags", []),
                }

                # Add Supabase enrichment if available
                if "supabase_data" in memory:
                    metadata["supabase"] = memory["supabase_data"]

                doc = Document(
                    page_content=content,
                    metadata=metadata,
                )
                documents.append(doc)

            logger.info(
                "memory_retriever_completed",
                user_id=self.user_id,
                documents_retrieved=len(documents),
            )

            return documents

        except Exception as e:
            logger.error(
                "memory_retriever_failed",
                error=str(e),
                user_id=self.user_id,
                exc_info=True,
            )
            return []


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

async def example_basic_retrieval():
    """Example: Basic memory retrieval."""
    from app.memory.unified_manager import get_memory_manager

    memory_manager = get_memory_manager()

    # Recall memories
    memories = await memory_manager.recall_memory(
        user_id="user-123",
        query="previous financing applications",
        session_id="session-456",
        tags=["prequalification"],
        limit=5,
    )

    print(f"Retrieved {len(memories)} memories:")
    for memory in memories:
        print(f"- {memory.get('content')[:100]}...")
        print(f"  Score: {memory.get('score')}")


async def example_langchain_chain():
    """Example: Using MemoryRetriever in a LangChain chain."""
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough

    # Create retriever
    retriever = MemoryRetriever(
        user_id="user-123",
        session_id="session-456",
        agent_name="financing",
        k=3,
    )

    # Create prompt template
    template = """You are a financing assistant for Ybryx Capital.

    Use the following context from previous interactions:
    {context}

    Current question: {question}

    Provide a helpful response based on the context and your knowledge.
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Create LLM - using GPT-5-nano for consistency
    from app.config import settings
    llm = ChatOpenAI(model=settings.openai_supervisor_model, temperature=0.7)

    # Format retrieved documents
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Build chain
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    # Invoke chain
    response = chain.invoke(
        "What equipment did I express interest in previously?"
    )

    print(f"Response: {response}")


async def example_reflection_query():
    """
    Example: Reflection pattern using memory recall.

    Agent reflects on past actions to improve future responses.
    """
    from app.memory.unified_manager import get_memory_manager

    memory_manager = get_memory_manager()

    # Query for similar past executions
    past_executions = await memory_manager.recall_memory(
        user_id="user-123",
        query="approved prequalification applications with high scores",
        tags=["prequalification", "approved"],
        limit=10,
    )

    # Analyze patterns
    patterns = {
        "common_industries": [],
        "average_revenue_range": [],
        "success_factors": [],
    }

    for execution in past_executions:
        content = execution.get("content", {})
        if isinstance(content, dict):
            # Extract patterns
            if "industry" in content:
                patterns["common_industries"].append(content["industry"])

            if "annual_revenue" in content:
                patterns["average_revenue_range"].append(content["annual_revenue"])

            if "success_factors" in content:
                patterns["success_factors"].extend(content["success_factors"])

    # Use patterns to inform current decision
    print("Learned patterns from past approvals:")
    print(f"Industries: {set(patterns['common_industries'])}")
    print(f"Revenue ranges: {set(patterns['average_revenue_range'])}")
    print(f"Success factors: {set(patterns['success_factors'])}")

    return patterns


async def example_goal_based_retrieval():
    """
    Example: Retrieve memories related to active goals.

    Demonstrates using goal vectors for semantic matching.
    """
    from app.memory.unified_manager import get_memory_manager

    memory_manager = get_memory_manager()

    # Load context with goals
    context = await memory_manager.load_context(
        user_id="user-123",
        session_id="session-456",
        include_goals=True,
    )

    # Get active goals
    goals = context.get("goals", [])

    if not goals:
        print("No active goals found")
        return

    # For each goal, retrieve related memories
    for goal in goals:
        goal_description = goal.get("goal_description", "")

        print(f"\nGoal: {goal_description}")
        print(f"Priority: {goal.get('priority')}/10")
        print(f"Progress: {goal.get('progress_percentage')}%")

        # Recall memories related to this goal
        related_memories = await memory_manager.recall_memory(
            user_id="user-123",
            query=goal_description,
            session_id="session-456",
            limit=5,
        )

        print(f"Related memories ({len(related_memories)}):")
        for memory in related_memories:
            print(f"- {memory.get('content', '')[:80]}...")


async def example_belief_graph_query():
    """
    Example: Query agent belief system.

    Demonstrates using belief vectors for reasoning.
    """
    from app.memory.unified_manager import get_memory_manager

    memory_manager = get_memory_manager()

    if not memory_manager.supabase:
        print("Supabase not configured")
        return

    # Query beliefs
    beliefs_response = memory_manager.supabase.table("belief_graphs").select("*").eq("user_id", "user-123").eq("agent_name", "financing").order("confidence_score", desc=True).limit(10).execute()

    beliefs = beliefs_response.data if beliefs_response.data else []

    print("Agent Beliefs (Financing):")
    for belief in beliefs:
        print(f"\n- {belief['belief_key']}")
        print(f"  Value: {belief['belief_value']}")
        print(f"  Confidence: {belief['confidence_score']:.2f}")
        print(f"  Evidence: {len(belief.get('evidence', []))} items")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    import asyncio

    print("=== Memory Retriever Examples ===\n")

    print("1. Basic Retrieval")
    asyncio.run(example_basic_retrieval())

    print("\n2. LangChain Chain Integration")
    asyncio.run(example_langchain_chain())

    print("\n3. Reflection Query")
    asyncio.run(example_reflection_query())

    print("\n4. Goal-Based Retrieval")
    asyncio.run(example_goal_based_retrieval())

    print("\n5. Belief Graph Query")
    asyncio.run(example_belief_graph_query())
