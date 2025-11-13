# Dependency Audit Report - Ybryx Capital
**Generated:** 2025-11-11
**Auditor:** Claude Code with Context7 MCP

## Executive Summary

This report analyzes all project dependencies against the latest stable releases and best practices from official documentation via Context7 MCP. **Critical updates are required** for security, stability, and access to new features.

---

## 🔴 CRITICAL FINDINGS

### 1. **Security Risk: API Keys in Version Control**
- **Severity:** CRITICAL
- **File:** `backend/.env`
- **Issue:** Real API keys committed to repository
  - OpenAI API Key: `sk-proj-_OfzNzEN0Fy...`
  - Anthropic API Key: `sk-ant-api03-HnPVTgd...`
  - Mem0 API Key: `m0-YJ41lrlr2oV...`
- **Action Required:**
  1. Rotate ALL keys immediately
  2. Remove from git history (use `git filter-branch` or BFG Repo-Cleaner)
  3. Add `.env` to `.gitignore` (if not already)
  4. Use `.env.example` for documentation only

### 2. **Runtime Error: Backend Won't Start**
- **Severity:** BLOCKING
- **File:** `backend/app/main.py:26`
- **Error:** `AttributeError: module 'structlog.stdlib' has no attribute 'INFO'`
- **Issue:** Invalid logging configuration
- **Fix:** Use Python's `logging` module constants, not `structlog.stdlib`

---

## 📦 BACKEND DEPENDENCIES (requirements.txt)

### Major Version Updates Required

| Package | Current | Latest Stable | Status | Breaking Changes? |
|---------|---------|---------------|--------|-------------------|
| **fastapi** | >=0.109.0 | **0.121.1** | ⚠️ UPDATE | Minor - Safe |
| **langgraph** | >=0.0.40 | **0.6.0** | 🔴 MAJOR UPDATE | YES - Review migration |
| **langchain** | >=0.1.0 | **1.0.5** | 🔴 MAJOR UPDATE | YES - v1.0 changes |
| **langchain-core** | Not specified | **1.0.4** | ⚠️ ADD | Required for v1.0 |
| **langchain-openai** | >=0.0.5 | **1.0.2** | 🔴 MAJOR UPDATE | YES |
| **langchain-anthropic** | >=0.1.0 | **1.0.2** | 🔴 MAJOR UPDATE | YES |
| **langgraph-checkpoint** | Not specified | **3.0.1** | ⚠️ ADD | New architecture |
| **langgraph-sdk** | Not specified | **0.2.9** | ⚠️ ADD | Cloud/API features |
| **pydantic** | >=2.5.0 | **2.12.4** | ✅ MINOR UPDATE | Safe |
| **pydantic-settings** | >=2.1.0 | **2.12.0** | ✅ MINOR UPDATE | Safe |
| **sqlalchemy** | >=2.0.25 | **2.0.44** | ✅ PATCH UPDATE | Safe |
| **uvicorn** | >=0.27.0 | **0.38.0** | ✅ MINOR UPDATE | Safe |

### Dependencies to Remove (Redundant per user request)
- ❌ **qdrant-client** - Redundant with Mem0
- ❌ **chromadb** - Redundant with Mem0
- ⚠️ **redis** - Evaluate if needed vs Supabase

### Dependencies to Add (Per LangGraph 0.6.0 requirements)

```txt
# LangGraph v1.0 Ecosystem
langgraph>=0.6.0
langgraph-checkpoint>=3.0.1
langgraph-sdk>=0.2.9
langgraph-prebuilt>=1.0.2

# LangChain v1.0 Ecosystem
langchain>=1.0.5
langchain-core>=1.0.4
langchain-openai>=1.0.2
langchain-anthropic>=1.0.2
langchain-community>=0.4.1
langchain-text-splitters>=1.0.0

# Required by LangGraph v0.6.0
orjson>=3.10.1
ormsgpack>=1.12.0
httpx>=0.28.0
tenacity>=9.0.0
structlog>=25.5.0
```

---

## 🌐 FRONTEND DEPENDENCIES (package.json)

### Major Version Updates Required

| Package | Current | Latest Stable | Status | Breaking Changes? |
|---------|---------|---------------|--------|-------------------|
| **next** | **13.5.1** | **15.4.0** | 🔴 MAJOR UPDATE | YES - App Router changes |
| **react** | **18.2.0** | **19.0.0** | 🔴 MAJOR UPDATE | YES - React 19 features |
| **react-dom** | **18.2.0** | **19.0.0** | 🔴 MAJOR UPDATE | Must match React |
| **@types/node** | 20.6.2 | 20.x (LTS) | ✅ CURRENT | Safe |
| **typescript** | 5.2.2 | 5.7.x | ⚠️ MINOR UPDATE | Review new features |
| **tailwindcss** | 3.3.3 | 4.0.0 | 🔴 MAJOR UPDATE | YES - Breaking changes |
| **@supabase/supabase-js** | 2.58.0 | 2.x | ✅ CURRENT | Check for patches |

### Next.js 13 → 15 Migration Considerations
- **App Router**: Already using App Router ✅
- **Turbopack**: New default dev bundler in v15
- **Server Actions**: Stable in v14+
- **Partial Prerendering**: New in v14+
- **React 19 Support**: Built-in v15

---

## 📋 RECOMMENDED MIGRATION PLAN

### Phase 1: Immediate (Security & Blocking Issues)
1. ✅ **Fix structlog error** (blocking)
2. ✅ **Rotate API keys** (security)
3. ✅ **Add email-validator** (already done)
4. ✅ **Remove API keys from git history**

### Phase 2: Backend Core Updates (1-2 days)
1. Update to **LangChain v1.0** ecosystem
2. Update to **LangGraph v0.6.0**
3. Update **FastAPI** to 0.121.1
4. Update **Pydantic** to 2.12.4
5. Run full test suite
6. Update documentation

### Phase 3: Frontend Updates (1-2 days)
1. Update **Next.js** 13.5.1 → 14.x first (test thoroughly)
2. Update **React** to 18.3.x (stable)
3. Consider **Next.js 15** migration (optional, test in branch)
4. Update **TypeScript** to 5.7.x
5. Update Radix UI components

### Phase 4: Cleanup & Optimization
1. Remove **qdrant-client** and **chromadb**
2. Evaluate **Redis** necessity
3. Configure **Mem0** to use Supabase pgvector
4. Update Docker images
5. Run integration tests

---

## 🔧 UPDATED REQUIREMENTS.TXT (Recommended)

```txt
# FastAPI & ASGI
fastapi>=0.121.0
uvicorn[standard]>=0.38.0
python-multipart>=0.0.20

# LangChain v1.0 Ecosystem
langchain>=1.0.5
langchain-core>=1.0.4
langchain-openai>=1.0.2
langchain-anthropic>=1.0.2
langchain-community>=0.4.1
langchain-text-splitters>=1.0.0

# LangGraph v1.0 Ecosystem
langgraph>=0.6.0
langgraph-checkpoint>=3.0.1
langgraph-sdk>=0.2.9
langgraph-prebuilt>=1.0.2

# Database & ORM
sqlalchemy>=2.0.44
alembic>=1.17.0
asyncpg>=0.30.0
psycopg2-binary>=2.9.11

# Supabase & Auth
supabase>=2.24.0
python-jose[cryptography]>=3.5.0
passlib[bcrypt]>=1.7.4

# Memory (Unified - Mem0 + Supabase only)
mem0ai>=1.0.0

# Data Validation & Settings
pydantic>=2.12.4
pydantic-core>=2.41.5
pydantic-settings>=2.12.0
email-validator>=2.3.0

# HTTP Client
httpx>=0.28.1
aiohttp>=3.13.2

# Logging & Monitoring
structlog>=25.5.0
python-json-logger>=4.0.0

# Serialization (Required by LangGraph)
orjson>=3.11.4
ormsgpack>=1.12.0

# Testing
pytest>=9.0.0
pytest-asyncio>=1.3.0
pytest-cov>=7.0.0
faker>=37.12.0

# Utilities
python-dotenv>=1.2.1
tenacity>=9.1.2
```

---

## 🔧 UPDATED PACKAGE.JSON (Recommended)

```json
{
  "name": "ybryx-frontend",
  "version": "0.2.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@hookform/resolvers": "^3.9.0",
    "@radix-ui/react-accordion": "^1.2.0",
    "@radix-ui/react-alert-dialog": "^1.1.1",
    "@radix-ui/react-avatar": "^1.1.0",
    "@radix-ui/react-checkbox": "^1.1.1",
    "@radix-ui/react-dialog": "^1.1.1",
    "@radix-ui/react-dropdown-menu": "^2.1.1",
    "@radix-ui/react-label": "^2.1.0",
    "@radix-ui/react-popover": "^1.1.1",
    "@radix-ui/react-select": "^2.1.1",
    "@radix-ui/react-separator": "^1.1.0",
    "@radix-ui/react-slider": "^1.2.0",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-switch": "^1.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-toast": "^1.2.1",
    "@radix-ui/react-tooltip": "^1.1.2",
    "@supabase/supabase-js": "^2.58.0",
    "@types/node": "^20.17.0",
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.1",
    "date-fns": "^3.6.0",
    "lucide-react": "^0.446.0",
    "next": "^14.2.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "react-hook-form": "^7.53.0",
    "tailwind-merge": "^2.5.2",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.7.0",
    "zod": "^3.23.8"
  }
}
```

---

## 🎯 BREAKING CHANGES TO REVIEW

### LangGraph 0.0.40 → 0.6.0
- **New checkpoint architecture** (langgraph-checkpoint package)
- **StateGraph API changes**
- **Memory management refactored**
- **SDK for cloud deployment** (langgraph-sdk)
- **Prebuilt agents** (langgraph-prebuilt package)

### LangChain 0.1.x → 1.0.x
- **Stable API** - Fewer breaking changes going forward
- **Improved tool calling**
- **Better streaming support**
- **Enhanced memory interfaces**
- **create_react_agent** standardization

### Next.js 13.5 → 15.x
- **Turbopack** default in dev (faster builds)
- **Partial Prerendering** (PPR) stable
- **React 19 support**
- **Enhanced caching semantics**
- **Improved TypeScript support**

---

## 📊 COMPATIBILITY MATRIX

| Backend Package | Min Python | Compatible With |
|----------------|------------|-----------------|
| FastAPI 0.121  | 3.8+       | Pydantic 2.12+  |
| LangGraph 0.6  | 3.9+       | LangChain 1.0+  |
| LangChain 1.0  | 3.9+       | Pydantic 2.5+   |
| Pydantic 2.12  | 3.8+       | All frameworks  |

| Frontend Package | Node Version | TypeScript |
|-----------------|--------------|------------|
| Next.js 14.x    | 18.17+       | 5.x        |
| Next.js 15.x    | 18.18+       | 5.x        |
| React 19        | 18.17+       | 5.x        |

---

## ✅ ACTION ITEMS

### Immediate (This Week)
- [ ] Fix structlog error in backend/app/main.py
- [ ] Rotate all API keys
- [ ] Remove keys from git history
- [ ] Test backend with current dependencies
- [ ] Update critical security patches

### Short Term (Next 2 Weeks)
- [ ] Migrate to LangChain v1.0
- [ ] Migrate to LangGraph v0.6.0
- [ ] Update FastAPI and Pydantic
- [ ] Remove redundant vector stores
- [ ] Configure Mem0 with Supabase pgvector

### Medium Term (Next Month)
- [ ] Update Next.js to 14.x
- [ ] Update React to 18.3.x
- [ ] Comprehensive integration testing
- [ ] Update documentation
- [ ] Performance benchmarking

### Long Term (Optional)
- [ ] Consider Next.js 15 migration
- [ ] Consider React 19 migration
- [ ] Explore Tailwind CSS 4

---

## 📚 MIGRATION RESOURCES

### Official Documentation (via Context7)
- **LangGraph v0.6.0**: `/langchain-ai/langgraph/0.6.0`
- **LangChain v1.0**: Migration guide in docs
- **FastAPI 0.118+**: `/fastapi/fastapi/0.118.2`
- **Next.js 14**: `/vercel/next.js/v14.3.0-canary.87`
- **Pydantic 2.12**: `/pydantic/pydantic`

### Testing Strategy
1. Create feature branch for updates
2. Update dependencies incrementally
3. Run test suite after each major update
4. Manual QA testing
5. Performance benchmarking
6. Merge to main after validation

---

## 💡 RECOMMENDATIONS

### High Priority
1. **Fix blocking runtime errors** before any dependency updates
2. **Rotate compromised API keys** immediately
3. **Update to LangGraph 0.6.0** for production stability
4. **Update to LangChain 1.0** for long-term API stability

### Medium Priority
5. **Remove redundant dependencies** (Qdrant, ChromaDB)
6. **Update FastAPI** for security patches
7. **Update Next.js to 14.x** for stability

### Low Priority
8. Consider Next.js 15 after 14.x is stable
9. Consider React 19 migration path
10. Explore Tailwind CSS 4 alpha

---

**Report End**
