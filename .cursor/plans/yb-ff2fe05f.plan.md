<!-- ff2fe05f-6257-455e-a3b0-1472c95c3924 df4fddee-5fe9-4db9-9cc9-44129b08f27b -->
# Ybryx Backend Scaffold Plan

## 1. Frontend Contract & Naming Audit

- Inventory data inputs/outputs from `frontend/app` (prequalify, robots, dealers, industries) to derive required API contracts.
- Flag all "Bolt" copy for update to "Ybryx" and define response payload shapes consumed by the UI.

## 2. Backend Project Skeleton

- Create `backend/pyproject.toml` (or `requirements.txt`) with FastAPI, LangGraph, LangChain, SQLAlchemy, asyncpg, mem0, supabase-py, pydantic-settings, httpx.
- Scaffold directory layout per standards:
- `backend/app/main.py`, `config.py`, `deps.py`
- `agents/`, `agents/supervisor/`, `agents/financing/`, `agents/dealer_matching/`
- `graph/` for LangGraph workflows & entrypoints
- `memory/`, `tools/`, `models/`, `database/`, `routers/`, `schemas/`, `services/`, `tests/`

## 3. Configuration & Persistence Layer

- Implement settings loader (`config.py`) honoring LLM priority, Supabase/Postgres, Mem0 env vars, feature flags.
- Define SQLAlchemy models & Alembic migrations for tenants, users, prequalifications, dealers, robots, threads, thread_messages, agent_versions (per Dev Standard).
- Add Supabase client wrapper for auth/RLS checks and async session utilities.

## 4. Agent Contracts, Memory, Tools

- Implement Pydantic agent contract models (`models/agent_contract.py`) mirroring JSON standard plus validation utilities.
- Build Mem0-backed `MemoryManager` matching Memory Management Standard with namespace isolation & composite scoring.
- Define LangChain-compatible tools (financial scoring, risk rules, dealer lookup, robot catalog search, notification stub) under `tools/` with structured schemas.

## 5. LangGraph Orchestration & Agent Hierarchy

- Design supervisor StateGraph orchestrator (`graph/supervisor.py`) using OpenAI gpt-5-nano for routing.
- Compose subgraphs:
- Financing Prequal Agent (Claude primary) with 5-node workflow (context, prompt, LLM, post-process, compliance triggers).
- Dealer Matching Agent using ToolNode for geospatial lookup + scheduling suggestions.
- Knowledge Agent for robot/industry insights retrieving Mem0 facts.
- Configure checkpointers, streaming, error recovery per Orchestration Standard.

## 6. FastAPI Surface & Services

- Map routers:
- `POST /api/v1/prequalifications` → invoke financing graph, persist application, return status token.
- `GET /api/v1/robots` with filters (search, category, use_case) backed by DB or agent tool.
- `GET /api/v1/dealers` (zip/pagination) + `POST /api/v1/dealers/match` to engage dealer agent.
- `GET /api/v1/industries` and `GET /api/v1/industries/{slug}` for UI content.
- `POST /api/v1/agents/{id}/chat` for future conversational UI.
- Implement service layer for prequalification scoring, dealer search, catalog queries, leveraging agents & tools.
- Ensure all responses return snake_case JSON matching frontend expectations & include Ybryx branding.

## 7. Observability, QA, and Ops

- Add logging/tracing config (structlog or standard logging) with node-level instrumentation.
- Define unit/integration test harness (pytest + httpx AsyncClient) covering workflows, routers, and memory manager stubs.
- Provide local dev instructions: `.env.example`, `docker-compose` for Postgres, Supabase CLI notes, `uvicorn` run command, plus CI checklist for lint/test.

### To-dos

- [ ] Document frontend data requirements and rename Bolt references to Ybryx in endpoints
- [ ] Create backend project structure, dependency manifests, and base config files
- [ ] Model database schema and Supabase/Postgres configuration with migrations
- [ ] Implement agent contracts, memory manager, tools, and LangGraph subgraphs
- [ ] Build FastAPI routers/services mapped to frontend flows and agent orchestration
- [ ] Set up logging, testing scaffolds, local dev instructions, and CI checklist