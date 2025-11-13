# Unified Memory System - Quick Start Guide

## Overview

The Ybryx Capital backend uses a **unified memory architecture** that integrates:
- **Supabase (PostgreSQL)** for structured, relational data
- **Mem0** for vector embeddings and semantic recall
- **MemoryManager** as the single authority for all memory operations

**Key Principle**: NO direct Supabase or Mem0 client access outside `unified_manager.py`.

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Required packages:
- `supabase>=2.3.0`
- `mem0ai>=0.0.5`
- `openai` (for embeddings)
- `tenacity` (for retries)

### 2. Configure Environment

Copy and configure environment variables:

```bash
cp .env.example .env
```

**Required variables**:

```env
# Supabase (REQUIRED)
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Mem0 (REQUIRED for vector operations)
MEM0_API_KEY=your_mem0_api_key
MEM0_BACKEND=pgvector

# OpenAI (REQUIRED for embeddings)
OPENAI_API_KEY=sk-...

# Vector Configuration
VECTOR_EMBEDDING_MODEL=text-embedding-3-large
VECTOR_EMBEDDING_DIMENSIONS=1536
```

### 3. Deploy Supabase Schema

Apply the database schema to your Supabase project:

**Option A: Supabase Dashboard**
1. Go to SQL Editor in Supabase dashboard
2. Copy contents of `supabase_schema.sql`
3. Execute

**Option B: Supabase CLI**
```bash
supabase db push < supabase_schema.sql
```

**Verify**:
```sql
-- Check tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

You should see:
- users
- sessions
- agent_executions
- memory_logs
- goal_assessments
- belief_graphs
- cognitive_metrics
- audit_logs

### 4. Test Connection

```python
from app.memory.unified_manager import get_memory_manager

# Initialize manager
memory_manager = get_memory_manager()

# Check connections
print(f"Supabase: {memory_manager.supabase is not None}")
print(f"Mem0: {memory_manager.mem0 is not None}")
print(f"Embedder: {memory_manager.embedder is not None}")
```

## Usage

### Basic Operations

#### 1. Create a Session

```python
from app.memory.unified_manager import get_memory_manager

memory_manager = get_memory_manager()

session_id = await memory_manager.create_session(
    user_id="user-123",
    agent_name="financing",
    client_info={
        "user_agent": "Mozilla/5.0",
        "ip": "192.168.1.1",
    },
)

print(f"Session created: {session_id}")
```

#### 2. Load Context

```python
context = await memory_manager.load_context(
    user_id="user-123",
    session_id=session_id,
    agent_name="financing",
    include_goals=True,
    include_beliefs=True,
    max_memories=10,
)

print(f"Loaded {len(context['recent_memories'])} memories")
print(f"Active goals: {len(context['goals'])}")
print(f"Beliefs: {len(context['beliefs'])}")
```

#### 3. Write Memory

```python
from datetime import datetime

payload = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "agent": "financing",
    "session_id": session_id,
    "type": "analysis_complete",
    "content": {
        "financial_score": 75,
        "recommendation": "approved",
        "lease_terms": {
            "monthly_payment": 1500,
            "term_months": 36,
        },
    },
}

result = await memory_manager.write_memory(
    user_id="user-123",
    session_id=session_id,
    payload=payload,
    memory_type="episodic",
    tags=["prequalification", "approved"],
)

print(f"Written to Supabase: {result['supabase_id']}")
print(f"Written to Mem0: {result['mem0_id']}")
```

#### 4. Recall Memory

```python
memories = await memory_manager.recall_memory(
    user_id="user-123",
    query="approved financing applications",
    session_id=session_id,
    tags=["approved"],
    limit=5,
)

for memory in memories:
    print(f"Content: {memory['content'][:100]}...")
    print(f"Score: {memory['score']}")
```

#### 5. Close Session

```python
await memory_manager.close_session(
    session_id=session_id,
    status="completed",
)
```

### Integration with LangGraph

#### Add Memory Nodes to Workflow

```python
from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import context_loader_node, memory_writer_node

# Create workflow
workflow = StateGraph(AgentState)

# Add memory nodes
workflow.add_node("load_context", context_loader_node)
workflow.add_node("agent", your_agent_node)
workflow.add_node("write_memory", memory_writer_node)

# Connect
workflow.set_entry_point("load_context")
workflow.add_edge("load_context", "agent")
workflow.add_edge("agent", "write_memory")
workflow.add_edge("write_memory", END)

# Compile
app = workflow.compile()

# Execute
result = await app.ainvoke({
    "user_id": "user-123",
    "application_id": session_id,
    "messages": [...],
})
```

#### Use Memory in Agent Node

```python
async def your_agent_node(state: AgentState) -> AgentState:
    # Access loaded context
    recent_memories = state.get("memory_context", [])
    active_goals = state.get("goals", [])

    # Use in reasoning
    context_summary = "\n".join([
        m.get("content", "") for m in recent_memories[:3]
    ])

    # ... agent logic

    return updated_state
```

## Advanced Usage

### LangChain Retriever Integration

```python
from app.examples.memory_retriever_example import MemoryRetriever
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Create retriever
retriever = MemoryRetriever(
    user_id="user-123",
    session_id=session_id,
    agent_name="financing",
    k=5,
)

# Use in chain
chain = (
    {"context": retriever, "question": ...}
    | prompt
    | llm
)

response = chain.invoke("What equipment was I interested in?")
```

### Goal-Based Retrieval

```python
# Load goals
context = await memory_manager.load_context(
    user_id="user-123",
    session_id=session_id,
    include_goals=True,
)

# For each active goal
for goal in context["goals"]:
    # Retrieve related memories
    related = await memory_manager.recall_memory(
        user_id="user-123",
        query=goal["goal_description"],
        limit=5,
    )

    # Use to assess goal progress
    print(f"Goal: {goal['goal_description']}")
    print(f"Progress: {goal['progress_percentage']}%")
    print(f"Related memories: {len(related)}")
```

### Memory Decay (Retention Policy)

```python
# Delete old memories
result = await memory_manager.decay_memory(
    user_id="user-123",
    threshold_days=30,
    memory_type="short_term",
)

print(f"Deleted {result['supabase_deleted']} records")
```

## Monitoring

### Query Recent Activity

```sql
-- Recent agent executions
SELECT * FROM recent_agent_activity
WHERE user_email = 'user@example.com'
LIMIT 10;

-- Memory operation summary
SELECT * FROM memory_operation_summary
WHERE operation_date > NOW() - INTERVAL '7 days';

-- User session stats
SELECT * FROM user_session_stats
WHERE email = 'user@example.com';
```

### Audit Logs

```python
# Query audit logs via Supabase
logs = memory_manager.supabase.table("audit_logs")\
    .select("*")\
    .eq("user_id", "user-123")\
    .order("timestamp", desc=True)\
    .limit(100)\
    .execute()

for log in logs.data:
    print(f"{log['timestamp']}: {log['event_type']}")
    print(f"  {log['message']}")
```

## Troubleshooting

### "Supabase not configured"
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`
- Use service role key (not anon key)
- Test connection: `supabase.table("users").select("count").execute()`

### "Mem0 not available"
- Install: `pip install mem0ai`
- Verify `MEM0_API_KEY` is set
- Check Mem0 dashboard for quota/status

### "JSONContract violation"
- Ensure payload includes all required fields:
  - `timestamp` (ISO8601)
  - `agent` (string)
  - `session_id` (string)
  - `type` (string)
  - `content` (dict)

### Memory not persisting
- Check RLS policies in Supabase
- Verify service role key permissions
- Check `audit_logs` table for errors

## Performance Tips

1. **Batch operations**: Use bulk inserts for multiple writes
2. **Cache sessions**: Store active session metadata in Redis
3. **Limit recall**: Use specific tags to narrow search space
4. **Index optimization**: Ensure vector indexes are built (`ivfflat`)
5. **Async everywhere**: Use async methods for all I/O

## Security Checklist

- [ ] Environment variables not committed to git
- [ ] Service role key secured (not anon key)
- [ ] RLS policies tested and enforced
- [ ] Audit logging enabled
- [ ] HTTPS enabled in production
- [ ] Regular key rotation scheduled

## Next Steps

1. **Read full documentation**: [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md)
2. **Review examples**: `app/examples/memory_retriever_example.py`
3. **Explore schema**: `supabase_schema.sql`
4. **Test integration**: Add memory nodes to your workflows
5. **Monitor usage**: Set up dashboards for memory metrics

## Support

For issues or questions:
- Check [MEMORY_SYSTEM.md](MEMORY_SYSTEM.md) for detailed architecture
- Review [Supabase Docs](https://supabase.com/docs)
- Review [Mem0 Docs](https://docs.mem0.ai)
- Check audit logs for error details
