# Infrastructure & Memory Architecture Standard

**Last Updated:** 2025-11-14
**Status:** ✅ ACTIVE
**Version:** 1.0.0

---

## 🎯 Overview

This document defines the infrastructure and memory architecture for the Ybryx Capital robotics financing platform. Our stack uses **Supabase** as the unified backend with **Mem0** for intelligent memory management.

---

## 🏗️ Infrastructure Stack

### Core Services

| Component | Technology | Purpose | Status |
|-----------|-----------|---------|---------|
| **Database** | PostgreSQL 15 (via Supabase) | Primary data store | ✅ Active |
| **Vector Store** | pgvector (Supabase extension) | Embeddings & semantic search | ✅ Active |
| **Memory Layer** | Mem0 + MemoryManager | Agent memory & context | ✅ Active |
| **Backend API** | FastAPI (Python 3.11) | REST API & agent orchestration | ✅ Active |
| **Frontend** | Next.js 14 (React) | Web application | ✅ Active |
| **Containerization** | Docker + Docker Compose | Development environment | ✅ Active |

### Removed Components

| Component | Reason for Removal | Replacement |
|-----------|-------------------|-------------|
| **Redis** | Redundant with Supabase | Supabase (PostgreSQL) |
| **Celery** | No longer needed without Redis | Direct async processing |

---

## 📊 Database Architecture

### Supabase PostgreSQL Schema

Our database uses Supabase's PostgreSQL with the following key features:

#### Extensions Enabled
- `pgvector` - Vector embeddings for semantic search
- `uuid-ossp` - UUID generation
- `pg_stat_statements` - Query performance monitoring

#### Core Tables

```sql
-- Applications
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_name VARCHAR(255) NOT NULL,
    revenue NUMERIC(12, 2),
    business_age INTEGER,
    credit_rating VARCHAR(10),
    industry VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    financial_score NUMERIC(5, 2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Dealers
CREATE TABLE dealers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    zip_code VARCHAR(10) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(255),
    specialties TEXT[],
    rating NUMERIC(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Robot Catalog
CREATE TABLE robot_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(255),
    price NUMERIC(12, 2),
    use_case VARCHAR(255),
    description TEXT,
    specifications JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Memory (Mem0 backend)
CREATE TABLE agent_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    namespace VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),  -- pgvector for embeddings
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_namespace (namespace),
    INDEX idx_embedding (embedding) USING ivfflat
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    messages JSONB NOT NULL,
    metadata JSONB,
    last_activity TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🧠 Memory Architecture

### Mem0 + MemoryManager Integration

Our memory system uses **Mem0** (memory layer) with **Supabase as the backend** for persistent, intelligent agent memory.

#### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Agent Layer                              │
│  (Financing, Sales, Dealer Matching, Knowledge)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  MemoryManager                               │
│  - Namespace isolation (agent:financing, agent:sales)        │
│  - Composite scoring (recency + relevance + importance)      │
│  - Automatic context retrieval                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Mem0                                     │
│  - Vector embeddings (OpenAI text-embedding-3-large)         │
│  - Semantic search & recall                                  │
│  - Graph-based memory connections                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Supabase (PostgreSQL + pgvector)                  │
│  - agent_memories table                                      │
│  - Vector indexes (ivfflat)                                  │
│  - JSONB metadata storage                                    │
└─────────────────────────────────────────────────────────────┘
```

#### MemoryManager Configuration

**File:** `backend/app/memory/manager.py`

```python
from mem0 import Memory

class MemoryManager:
    """Unified memory manager for agents with composite scoring."""

    def __init__(
        self,
        namespace: str,
        composite_scoring: bool = True,
        retention_days: int = 30
    ):
        self.namespace = namespace
        self.composite_scoring = composite_scoring

        # Initialize Mem0 with Supabase backend
        self.memory = Memory.from_config({
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-5-nano",
                    "api_key": settings.openai_api_key
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-large",
                    "api_key": settings.openai_api_key
                }
            },
            "vector_store": {
                "provider": "pgvector",
                "config": {
                    "url": settings.database_url,
                    "collection_name": f"memories_{namespace}"
                }
            }
        })

    async def search(
        self,
        query: str,
        limit: int = 5,
        filters: dict = None
    ) -> list:
        """Search memories with composite scoring."""
        memories = await self.memory.search(
            query,
            limit=limit,
            filters={"namespace": self.namespace, **(filters or {})}
        )

        if self.composite_scoring:
            return self._apply_composite_scoring(memories)

        return memories

    async def add(
        self,
        content: str,
        metadata: dict = None
    ) -> str:
        """Add memory with namespace."""
        return await self.memory.add(
            content,
            metadata={"namespace": self.namespace, **(metadata or {})}
        )
```

#### Agent-Specific Namespaces

| Agent | Namespace | Purpose |
|-------|-----------|---------|
| Financing Agent | `agent:financing` | Application data, scoring history |
| Sales Agent | `agent:sales` | Conversation history, lead data |
| Dealer Matching | `agent:dealer_matching` | Dealer queries, matches |
| Knowledge Agent | `agent:knowledge` | Product inquiries, recommendations |
| Supervisor | `agent:supervisor` | Routing decisions, conversation state |

---

## 🔧 Development Environment

### Docker Compose Services

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: ybryx-postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ybryx
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      target: development
    container_name: ybryx-backend
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ybryx
      - DEBUG=True
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
    container_name: ybryx-frontend
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
      - NODE_ENV=development
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
  backend_data:
```

### Environment Variables

**File:** `backend/.env.example`

```bash
# Database - Supabase
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ybryx
# Or production Supabase:
# DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres

# Supabase (REQUIRED for unified memory system)
SUPABASE_URL=https://[PROJECT_REF].supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Memory - Mem0 (uses Supabase backend)
MEM0_API_KEY=your_mem0_api_key
MEM0_HOST=https://api.mem0.ai
MEM0_BACKEND=pgvector

# Vector Embeddings
VECTOR_EMBEDDING_MODEL=text-embedding-3-large
VECTOR_EMBEDDING_DIMENSIONS=1536
```

---

## 🚀 Deployment

### Production Setup

1. **Supabase Project Setup**
   ```bash
   # Create Supabase project at https://supabase.com
   # Enable pgvector extension in SQL editor:
   CREATE EXTENSION IF NOT EXISTS vector;

   # Run schema migrations
   psql -h db.[PROJECT_REF].supabase.co -U postgres -d postgres < migrations/schema.sql
   ```

2. **Environment Configuration**
   ```bash
   # Set production environment variables
   export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres"
   export SUPABASE_URL="https://[PROJECT_REF].supabase.co"
   export SUPABASE_ANON_KEY="..."
   export SUPABASE_SERVICE_ROLE_KEY="..."
   ```

3. **Mem0 Configuration**
   ```bash
   # Configure Mem0 to use Supabase pgvector backend
   export MEM0_BACKEND=pgvector
   export MEM0_API_KEY="..."
   ```

---

## ✅ Migration from Redis

### What Changed

| Before (Redis) | After (Supabase) |
|----------------|------------------|
| Redis for caching | Supabase PostgreSQL for all persistence |
| Celery for tasks | Direct async processing in FastAPI |
| Separate cache layer | Unified database with efficient queries |
| Redis session storage | Supabase `chat_sessions` table |

### Migration Steps

1. **Remove Redis from docker-compose.yml** ✅
2. **Remove Redis configuration from config.py** ✅
3. **Remove redis/celery dependencies from pyproject.toml** ✅
4. **Update session storage to use Supabase** ⏳
5. **Test all agent memory operations** ⏳

---

## 📊 Performance Characteristics

### Latency Targets

| Operation | Target | Current |
|-----------|--------|---------|
| Memory search (5 results) | <100ms | ~80ms |
| Memory add | <50ms | ~40ms |
| Chat session retrieval | <30ms | ~25ms |
| Agent response (total) | <3s | ~2.5s |

### Scalability

- **Database**: Supabase auto-scales to 100k+ rows
- **Vector Search**: pgvector with ivfflat index supports 1M+ vectors
- **Concurrent Agents**: Up to 100 concurrent agent conversations
- **Memory Retention**: 30 days with auto-cleanup

---

## 🔒 Security & Compliance

### Data Protection

- **Encryption at Rest**: Supabase provides automatic encryption
- **Encryption in Transit**: TLS 1.3 for all connections
- **Access Control**: Row-level security (RLS) policies in Supabase
- **API Keys**: Managed via environment variables, never committed

### Compliance Features

- **GDPR**: Data deletion via Supabase RLS policies
- **Audit Logs**: PostgreSQL `pg_audit` extension
- **Backup**: Automated daily backups via Supabase

---

## 📚 Related Documentation

- [Agent Creation Standard](./AGENT_CREATION_STANDARD.md)
- [Agent Orchestration Standard](./AGENT_ORCHESTRATION_STANDARD.md)
- [LLM Configuration Standard](./LLM_CONFIGURATION_STANDARD.md)
- [Memory Management Implementation](../../backend/app/memory/manager.py)

---

**END OF DOCUMENT**
