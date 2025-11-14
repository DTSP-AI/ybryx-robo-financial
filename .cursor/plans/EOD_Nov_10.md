You are operating under the Agentic Systems Infrastructure Standards, including:

AGENT_CREATION_STANDARD.md

AGENT_ORCHESTRATION_STANDARD.md

AGENT_JSONCONTRACT1st_IDENTITY-RESPONSE_STNDRD.md

MEMORY_MANAGEMENT_STANDARD.md

LLM_CONFIGURATION_STANDARD.md

Your task is to build a Supabase + Mem0 integrated backend foundation where all memory operations—vector or relational—flow through a single unified memory_manager.py module.
No extra wrappers or isolated client files should be created unless required by dependency injection (e.g., Supabase SDK).

⚙️ OBJECTIVE

Create a production-grade, LangGraph-compatible memory system for the YBRYX Robotics agent stack, powered by:

Supabase (PostgreSQL) → Persistent structured storage (auth, sessions, metrics, logs)

Mem0 (PGVector or FAISS) → Vectorized long/short-term memory, context recall

memory_manager.py → Unified abstraction layer coordinating both systems

FastAPI backend → Provides endpoints for LangGraph agent access to memory + state

LangGraph Nodes → Read/write context exclusively via memory_manager.py methods

🧩 SYSTEM DESIGN REQUIREMENTS
🔐 Supabase Responsibilities

Use Supabase for structured, relational, and transactional data:

users → Auth, profiles, role metadata (secured by RLS)

sessions → Active session IDs, start/end times, client info

agent_executions → Tracks all agent runs, timestamps, summaries

memory_logs → Record of all memory write/recall operations

goal_assessments, belief_graphs, cognitive_metrics → Tables as defined in MEMORY_MANAGEMENT_STANDARD.md

audit_logs → Full traceability for agent actions

files (optional) → Use Supabase Storage for PDFs, audio, uploads

🧠 Mem0 Responsibilities

Use Mem0 for:

Long-term and short-term memory vectors

Context recall and embedding-based retrieval

Agent “beliefs,” “goals,” and “reflections” stored as structured embeddings

Chunked content vectors with metadata: user_id, session_id, agent_name, tags

🧠 memory_manager.py (Unified Controller)

This file is the sole authority for all memory operations.
It should manage both Supabase (relational) and Mem0 (vector) interactions internally.

Core Classes & Methods
class MemoryManager:
    def __init__(self, supabase_client, mem0_client, embedder):
        self.supabase = supabase_client
        self.mem0 = mem0_client
        self.embedder = embedder

    # 1. Load contextual memory
    async def load_context(self, user_id: str, session_id: str) -> dict:
        """
        Retrieves the contextual snapshot for an agent's runtime.
        Pulls vector context from Mem0 and structured session data from Supabase.
        """
        ...

    # 2. Write memory updates
    async def write_memory(self, user_id: str, session_id: str, payload: dict) -> None:
        """
        Writes new memory to Supabase (structured) and Mem0 (vector) simultaneously.
        Ensures JSONContract compliance for all writes.
        """
        ...

    # 3. Recall by tag or query
    async def recall_memory(self, user_id: str, query: str, tags: list = None) -> list:
        """
        Vector similarity recall from Mem0 with optional Supabase log enrichment.
        """
        ...

    # 4. Log and audit
    async def log_event(self, user_id: str, event_type: str, data: dict) -> None:
        """
        Writes all significant memory or agent events to Supabase audit_logs.
        """
        ...

    # 5. Purge or decay old memory
    async def decay_memory(self, user_id: str, threshold_days: int) -> None:
        """
        Trims or decays vector memory beyond a set retention window.
        """
        ...

Key Rules

✅ Every write/read event must pass through MemoryManager

✅ All payloads must match JSONContract schema (identity, timestamp, agent_name)

✅ Wrap all Supabase + Mem0 calls in retry decorators from AGENT_CREATION_STANDARD.md

✅ Include structured exception handling + logging to Supabase’s audit_logs

✅ No standalone mem0_client.py or supabase_client.py; initialize SDKs in the manager

🧰 DEPENDENCIES & CONFIGURATION

Environment variables (.env.example):

SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
MEM0_API_KEY=
MEM0_BACKEND=pgvector
OPENAI_API_KEY=
VECTOR_EMBEDDING_MODEL=text-embedding-3-large


SDK Initialization (inside memory_manager.py):

from supabase import create_client
from mem0 import Mem0Client
from openai import OpenAI

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
mem0 = Mem0Client(api_key=os.getenv("MEM0_API_KEY"))
embedder = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

🧠 DATABASE & VECTOR SCHEMA OUTPUTS

Claude should output:

supabase_schema.sql — full table creation, indexes, and RLS rules

memory_manager.py — complete unified implementation

.env.example — all keys used

Integration example for LangGraph node (context_loader_node.py) showing MemoryManager.load_context()

Integration example for LangChain retriever usage (e.g., reflection query)

🧩 ADDITIONAL IMPLEMENTATION RULES

Use async/await everywhere.

Follow retry & error patterns from AGENT_CREATION_STANDARD.md.

Memory payloads must include:
{ "identity": str, "timestamp": str, "agent": str, "session_id": str, "type": str, "content": dict }

Never store duplicate data across Supabase + Mem0.

Supabase = event & audit metadata

Mem0 = embeddings and contextual representations

Every successful write must trigger an audit log in Supabase.

Maintain modular import readiness for Docker Compose and FastAPI router inclusion.

⚡ DELIVERABLES FROM CLAUDE

When this prompt runs, Claude should output:

memory_manager.py — unified controller class

supabase_schema.sql — all tables, constraints, and RLS rules

.env.example

Sample integration code:

context_loader_node.py → reads via MemoryManager.load_context()

memory_writer_node.py → writes via MemoryManager.write_memory()

README.md explaining architectural overview and environment setup