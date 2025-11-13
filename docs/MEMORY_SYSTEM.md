# Unified Memory System Architecture

## Overview

The Ybryx Capital agent system uses a **unified memory architecture** that integrates Supabase (PostgreSQL) for structured data and Mem0 for vector embeddings and semantic recall.

**Key Principle**: All memory operations flow through a single `MemoryManager` class. No direct client access.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│           LangGraph Agent Nodes                     │
│  (context_loader, memory_writer, agents)            │
└────────────────┬────────────────────────────────────┘
                 │
                 │ All memory operations
                 │
        ┌────────▼────────┐
        │ MemoryManager   │  ← SINGLE AUTHORITY
        │ (unified_manager.py) │
        └────────┬────────┘
                 │
         ┌───────┴────────┐
         │                │
    ┌────▼─────┐    ┌────▼────┐
    │ Supabase │    │  Mem0   │
    │  (PostgreSQL) │    │ (Vector) │
    └──────────┘    └─────────┘
```

## Component Responsibilities

### Supabase (Structured/Relational)
Handles all persistent, structured data:

- **Users**: Auth, profiles, roles (with RLS)
- **Sessions**: Active/historical agent sessions
- **Agent Executions**: Performance metrics, timing, status
- **Memory Logs**: Audit trail of all memory operations
- **Goal Assessments**: Agent goals with vector embeddings
- **Belief Graphs**: Agent belief system with confidence scores
- **Cognitive Metrics**: Performance tracking
- **Audit Logs**: Complete system audit trail

**Tables Created**: See `supabase_schema.sql`

### Mem0 (Vector/Semantic)
Handles all embedding-based operations:

- **Long-term memory**: Persistent vector storage
- **Short-term memory**: Session-scoped vectors
- **Context recall**: Semantic similarity search
- **Agent beliefs/goals**: Embedded as vectors for similarity matching
- **Chunked content**: Document/conversation chunks with metadata

**Configuration**: PGVector backend recommended for production

### MemoryManager (Unified Controller)
Single point of control for all memory operations:

**Core Methods**:
- `load_context()` - Load session context at start
- `write_memory()` - Write to both Supabase + Mem0
- `recall_memory()` - Semantic search with enrichment
- `log_event()` - Audit logging
- `decay_memory()` - Retention policy enforcement
- `create_session()` - Session management
- `log_agent_execution()` - Execution tracking

## Database Schema

### Key Tables

#### sessions
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key to users)
- session_id: TEXT (external identifier)
- agent_name: TEXT
- status: TEXT (active, completed, failed, timeout)
- started_at, ended_at: TIMESTAMPTZ
- client_info, context: JSONB
```

#### memory_logs
```sql
- id: UUID
- user_id, session_id: UUID
- agent_name: TEXT
- operation_type: TEXT (write, read, recall, decay, delete)
- memory_type: TEXT (short_term, long_term, episodic, semantic, procedural)
- content: TEXT
- vector_id: TEXT (reference to Mem0)
- tags: TEXT[]
- metadata: JSONB
```

#### goal_assessments
```sql
- id: UUID
- user_id, session_id: UUID
- goal_description: TEXT
- goal_vector: VECTOR(1536)  -- pgvector
- priority: INTEGER (1-10)
- status: TEXT (active, achieved, abandoned, blocked)
- progress_percentage: INTEGER
```

#### belief_graphs
```sql
- id: UUID
- user_id, session_id: UUID
- belief_key, belief_value: TEXT
- belief_vector: VECTOR(1536)
- confidence_score: FLOAT (0-1)
- evidence: JSONB
- related_beliefs: TEXT[]
```

### Row-Level Security (RLS)

All tables implement RLS:
- Users can only access their own data
- System/admin roles have elevated access
- Service role (backend) has full access
- Audit logs are admin-only

## JSONContract Compliance

All memory writes must conform to the JSONContract standard:

```json
{
  "timestamp": "2025-01-10T12:00:00Z",
  "agent": "financing_agent",
  "session_id": "uuid-string",
  "type": "agent_execution_result",
  "content": {
    "role": "assistant",
    "content": "Analysis complete...",
    "tool_calls": [],
    "execution_summary": {}
  }
}
```

**Validation**: Automatic via `validate_jsoncontract()` function

## Usage Examples

### 1. Context Loading (Start of Agent Execution)

```python
from app.memory.unified_manager import get_memory_manager

async def my_agent_node(state: AgentState):
    memory_manager = get_memory_manager()

    # Load full context
    context = await memory_manager.load_context(
        user_id=state["user_id"],
        session_id=state["application_id"],
        agent_name="financing",
        include_goals=True,
        include_beliefs=True,
        max_memories=10,
    )

    # Use context in agent reasoning
    recent_memories = context["recent_memories"]
    active_goals = context["goals"]

    # ... agent logic

    return updated_state
```

### 2. Memory Writing (End of Agent Execution)

```python
from app.memory.unified_manager import get_memory_manager

async def write_execution_memory(state: AgentState):
    memory_manager = get_memory_manager()

    # Construct JSONContract payload
    payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": "financing",
        "session_id": state["application_id"],
        "type": "prequalification_analysis",
        "content": {
            "financial_score": 75,
            "recommendation": "approved",
            "terms": {...}
        }
    }

    # Write to both Supabase and Mem0
    result = await memory_manager.write_memory(
        user_id=state["user_id"],
        session_id=state["application_id"],
        payload=payload,
        memory_type="episodic",
        tags=["prequalification", "approved"],
    )

    # Result contains both IDs
    # result["supabase_id"], result["mem0_id"]
```

### 3. Semantic Recall

```python
# Search for similar memories
memories = await memory_manager.recall_memory(
    user_id="user-123",
    query="previous prequalification approvals",
    session_id="session-456",  # optional
    tags=["prequalification", "approved"],
    limit=5,
)

for memory in memories:
    print(memory["content"])
    print(memory["score"])  # similarity score
    if "supabase_data" in memory:
        print(memory["supabase_data"])  # enriched metadata
```

### 4. Session Management

```python
# Create session
session_id = await memory_manager.create_session(
    user_id="user-123",
    agent_name="financing",
    client_info={"user_agent": "Mozilla/5.0", "ip": "1.2.3.4"},
)

# ... agent execution

# Close session
await memory_manager.close_session(
    session_id=session_id,
    status="completed",
)
```

### 5. Memory Decay (Retention Policy)

```python
# Delete memories older than 30 days
result = await memory_manager.decay_memory(
    user_id="user-123",
    threshold_days=30,
    memory_type="short_term",  # optional filter
)

print(f"Deleted {result['supabase_deleted']} Supabase records")
print(f"Deleted {result['mem0_deleted']} Mem0 vectors")
```

## Integration with LangGraph

### Adding Memory Nodes to Workflow

```python
from langgraph.graph import StateGraph
from app.graph.nodes import context_loader_node, memory_writer_node

# Create workflow
workflow = StateGraph(AgentState)

# Add memory nodes
workflow.add_node("load_context", context_loader_node)
workflow.add_node("write_memory", memory_writer_node)

# Set entry point
workflow.set_entry_point("load_context")

# Add agent nodes
workflow.add_node("financing_agent", financing_node)

# Connect nodes
workflow.add_edge("load_context", "financing_agent")
workflow.add_edge("financing_agent", "write_memory")
workflow.add_edge("write_memory", END)

# Compile
app = workflow.compile()
```

### State Schema

Your `AgentState` should include:

```python
class AgentState(TypedDict):
    user_id: str  # REQUIRED
    application_id: str  # Used as session_id
    messages: list
    current_agent: str

    # Memory fields (populated by context_loader)
    memory_context: list[dict]
    goals: list[dict]
    beliefs: list[dict]
    session_metadata: dict

    # Memory write tracking
    memory_written: bool
    memory_write_result: dict
```

## Error Handling & Retries

The MemoryManager includes automatic retry logic (from AGENT_CREATION_STANDARD.md):

- **Max attempts**: 3
- **Exponential backoff**: 2s, 4s, 8s
- **Retryable errors**: ConnectionError, TimeoutError
- **Logging**: All failures logged to audit_logs

```python
@retry_on_failure(max_attempts=3)
async def load_context(...):
    # Auto-retries on transient failures
    ...
```

## Security Considerations

### Row-Level Security (RLS)
- All Supabase tables use RLS
- Users can only access their own data
- Service role bypasses RLS for backend operations

### API Keys
- Store in `.env`, never commit
- Use service role key for backend (not anon key)
- Rotate keys regularly

### Audit Logging
- All memory operations logged to `audit_logs`
- Includes user_id, timestamp, IP, operation type
- Immutable audit trail

## Performance Optimization

### Indexing
All critical columns indexed:
- `user_id`, `session_id` on all tables
- `timestamp` DESC for recent queries
- GIN indexes on JSONB and array columns
- IVFFlat indexes on vector columns

### Caching
Consider Redis for:
- Session metadata (hot data)
- Recent memories (avoid duplicate Mem0 calls)
- User preferences

### Batch Operations
For bulk memory writes:
```python
# Batch insert to Supabase
supabase.table("memory_logs").insert([...]).execute()

# Batch add to Mem0
mem0.add_batch([...])
```

## Monitoring & Observability

### Key Metrics to Track

1. **Memory Operations**:
   - Write latency (p50, p95, p99)
   - Read latency
   - Recall accuracy (relevance scores)

2. **Storage Growth**:
   - Mem0 vector count per user
   - Supabase table sizes
   - Decay operation frequency

3. **Error Rates**:
   - Failed writes
   - Timeouts
   - JSONContract violations

### Queries

```sql
-- Recent memory activity
SELECT * FROM recent_agent_activity LIMIT 100;

-- Memory operation summary
SELECT * FROM memory_operation_summary
WHERE operation_date > NOW() - INTERVAL '7 days';

-- User session stats
SELECT * FROM user_session_stats;

-- Error audit
SELECT * FROM audit_logs
WHERE severity IN ('error', 'critical')
ORDER BY timestamp DESC;
```

## Deployment Checklist

- [ ] Supabase project created
- [ ] Schema deployed (`supabase_schema.sql`)
- [ ] RLS policies tested
- [ ] Mem0 account configured (PGVector backend)
- [ ] Environment variables set
- [ ] Service role key secured
- [ ] Indexes created and optimized
- [ ] Monitoring/alerting configured
- [ ] Backup strategy defined
- [ ] Memory decay policy configured

## Troubleshooting

### Common Issues

**"Supabase not configured"**
- Check `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`
- Verify service role key (not anon key)

**"Mem0 not available"**
- Install: `pip install mem0ai`
- Check `MEM0_API_KEY` is set
- Verify Mem0 backend configuration

**"JSONContract violation"**
- Ensure all payloads include: timestamp, agent, session_id, type, content
- Timestamp must be ISO8601 format
- Content must be a dict

**Slow memory recall**
- Check Mem0 vector index health
- Reduce `limit` parameter
- Add more specific tags/filters
- Consider caching frequent queries

**Memory not persisting**
- Check Supabase connection
- Verify user has write permissions (RLS)
- Check audit_logs for errors

## Migration from Old System

If migrating from the previous `manager.py`:

1. **Update imports**:
   ```python
   # Old
   from app.memory.manager import MemoryManager

   # New
   from app.memory.unified_manager import get_memory_manager
   memory_manager = get_memory_manager()
   ```

2. **Update method calls**:
   - Old `add()` → New `write_memory()`
   - Old `search()` → New `recall_memory()`
   - Add JSONContract wrapper to all writes

3. **Session management**:
   - Create sessions explicitly with `create_session()`
   - Track session_id in state

4. **Test thoroughly**:
   - Verify RLS policies don't block operations
   - Check Mem0 metadata format
   - Validate audit logging

## Further Reading

- [MEMORY_MANAGEMENT_STANDARD.md](../Dev_Standard/MEMORY_MANAGEMENT_STANDARD.md)
- [AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md](../Dev_Standard/AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md)
- [Supabase Documentation](https://supabase.com/docs)
- [Mem0 Documentation](https://docs.mem0.ai)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
