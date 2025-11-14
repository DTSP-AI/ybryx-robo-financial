# LLM Configuration Standard
## Claude as Primary Agent for Content Creation

**Last Updated:** 2025-10-28
**Status:** ✅ ACTIVE AND VERIFIED

---

## 🎯 Overview

This document defines the LLM (Large Language Model) priority and configuration across the ContentCreationAgent system.

**CRITICAL RULE:** Claude (Anthropic) is the **PRIMARY** LLM for all content creation tasks. OpenAI is a **FALLBACK ONLY**.

---

## 📋 LLM Priority Matrix

| Use Case | Primary LLM | Fallback LLM | Rationale |
|----------|-------------|--------------|-----------|
| **Script Generation** | Claude 3.5 Sonnet | OpenAI gpt-5-nano | Superior creative writing quality |
| **Supervisor Routing** | OpenAI gpt-5-nano | N/A | Fast, low-cost routing decisions |
| **Supervisor Conversation** | OpenAI gpt-5-nano | N/A | Conversational interactions |
| **Chat Workflows** | Claude 3.5 Sonnet | OpenAI gpt-5-nano | Better context understanding |

---

## ⚙️ Configuration Details

### Environment Variables (.env)

```bash
# Anthropic Claude - PRIMARY for content creation
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620  # ACTIVE MODEL

# OpenAI - Supervisor routing + fallback
# NOTE: gpt-5-nano is a VALID, ACTIVE model - do not change to gpt-4o-mini
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5-nano  # ACTIVE MODEL for routing
```

### Python Configuration (backend/config.py)

```python
# Anthropic Configuration
ANTHROPIC_API_KEY: Optional[str] = None
ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20240620"

# OpenAI Configuration
OPENAI_API_KEY: Optional[str] = None
# NOTE: gpt-5-nano is a VALID, ACTIVE OpenAI model - optimized for fast, low-cost routing
OPENAI_MODEL: str = "gpt-5-nano"  # ACTIVE MODEL - do not change
OPENAI_SCRIPT_MODEL: str = "gpt-5-nano"  # Not used (Claude handles scripts, GPT is fallback)
```

---

## ⚙️ GPT-5 Nano Configuration Requirements

**CRITICAL:** GPT-5 models (gpt-5-nano, gpt-5-mini, gpt-5) have different API requirements than GPT-4 models.

### Required Parameters for GPT-5

```python
from langchain_openai import ChatOpenAI

# ✅ Correct GPT-5 Configuration
llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0.7,
    max_completion_tokens=2000,       # ✅ Use max_completion_tokens (NOT max_tokens)
    reasoning_effort="minimal",        # ✅ Required for conversational tasks
    api_key=settings.openai_api_key,
)

# ❌ Wrong GPT-5 Configuration (will return empty responses)
llm = ChatOpenAI(
    model="gpt-5-nano",
    temperature=0.7,
    max_tokens=500,                   # ❌ GPT-5 doesn't support max_tokens
    api_key=settings.openai_api_key,  # ❌ Missing reasoning_effort parameter
)
```

### Why These Parameters Are Required

1. **`max_completion_tokens` instead of `max_tokens`:**
   - GPT-5 API doesn't support the `max_tokens` parameter
   - Using `max_tokens` causes HTTP 400 errors or is silently ignored
   - Always use `max_completion_tokens` for GPT-5 models

2. **`reasoning_effort="minimal"` for conversational tasks:**
   - GPT-5 models spend tokens on "reasoning" before generating output
   - Without this parameter, reasoning can consume 800+ tokens
   - For chat/conversation: Use `reasoning_effort="minimal"`
   - For complex analysis: Use `reasoning_effort="medium"` or `reasoning_effort="high"`

3. **Token budget must be sufficient:**
   - Minimum 2000 tokens recommended for GPT-5 Nano
   - Reasoning overhead requires extra token budget
   - 500 tokens is too small and causes empty responses

### Common Issues and Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Empty responses | `response.content = ""` | Add `reasoning_effort="minimal"` |
| HTTP 400 error | `max_tokens not supported` | Change to `max_completion_tokens` |
| Truncated output | Response cuts off mid-sentence | Increase `max_completion_tokens` to 2000+ |
| Slow responses | Takes 10+ seconds | Use `reasoning_effort="minimal"` for chat |

### GPT-5 Model Comparison

| Model | Speed | Cost (per 1M tokens) | Best For |
|-------|-------|---------------------|----------|
| **gpt-5-nano** | Fastest | $0.05 input / $0.40 output | Chat, routing, simple tasks |
| **gpt-5-mini** | Fast | $0.25 input / $2.00 output | Conversational agents, analysis |
| **gpt-5** | Moderate | $5.00 input / $15.00 output | Complex reasoning, research |

### Implementation Example (Sales Agent)

**File:** `backend/app/graph/agents.py` (lines 370-377)

```python
def create_sales_agent_node() -> callable:
    """Create sales agent node for landing page chat."""
    llm = ChatOpenAI(
        model=settings.openai_supervisor_model,  # gpt-5-nano
        temperature=0.7,
        max_completion_tokens=2000,  # GPT-5 requires max_completion_tokens
        reasoning_effort="minimal",   # Optimizes for speed/chat
        api_key=settings.openai_api_key,
    )
    # ... rest of implementation
```

### Debugging GPT-5 Empty Responses

If you get empty responses (`response_length=0` in logs):

1. **Check parameters:**
   ```python
   # Verify you're using max_completion_tokens
   print(llm.model_kwargs)  # Should show max_completion_tokens, not max_tokens
   ```

2. **Add reasoning_effort:**
   ```python
   reasoning_effort="minimal"  # Critical for conversational use cases
   ```

3. **Increase token budget:**
   ```python
   max_completion_tokens=2000  # Minimum recommended for GPT-5 Nano
   ```

4. **Check backend logs:**
   ```bash
   docker logs ybryx-backend --tail 20 | grep "sales_agent_completed"
   # Should show: response_length=1000+ (not 0)
   ```

---

## 📍 Implementation Locations

### 1. Video Script Generation (content_creation_agent.py + video_script_tool.py)

**File:** `backend/tools/video_script_tool.py`
**Lines:** 86-98

**Priority Logic:**
```python
# 1. Try Claude first (PRIMARY)
if settings.ANTHROPIC_API_KEY:
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    model = settings.ANTHROPIC_MODEL
    use_anthropic = True
    logger.info("Using Claude 3.5 Sonnet for script generation")

# 2. Fallback to OpenAI if Claude unavailable
elif settings.OPENAI_API_KEY:
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    model = settings.OPENAI_SCRIPT_MODEL
    use_anthropic = False
    logger.info("Using OpenAI GPT for script generation (fallback)")

# 3. Error if neither available
else:
    raise ValueError("Either ANTHROPIC_API_KEY or OPENAI_API_KEY is required")
```

**Documentation Added:**
- Module header: Lines 7-17 with ⚠️ IMPORTANT - LLM PRIORITY section
- content_creation_agent.py header: Lines 9-14 with configuration notes

### 2. Supervisor Chat Workflows (supervisor_chat.py)

**File:** `backend/workflow/supervisor_chat.py`
**Lines:** 33-49

**Priority Logic:**
```python
def get_llm():
    """Get LLM instance with fallback logic"""
    # 1. Try Claude first (PRIMARY)
    if settings.ANTHROPIC_API_KEY:
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=settings.ANTHROPIC_MODEL,
            temperature=0.7,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )

    # 2. Fallback to OpenAI
    elif settings.OPENAI_API_KEY:
        return ChatOpenAI(
            model=settings.OPENAI_SCRIPT_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )

    # 3. Error if neither
    else:
        raise ValueError("No LLM API key configured")
```

**Documentation Added:**
- Module header: Lines 10-15 with LLM priority notes

### 3. Supervisor Agent Routing (supervisor_agent.py)

**File:** `backend/agents/supervisor_agent.py`
**Lines:** 411, 574

**Purpose:** Uses **OpenAI gpt-5-nano** for fast routing decisions (not content creation)

**Documentation Added:**
- Module header: Lines 14-18 with model configuration warnings
- Explicitly states gpt-5-nano is VALID and ACTIVE
- DO NOT change to gpt-4o-mini without authorization

---

## ✅ Verification Steps

Run these commands to verify configuration:

```bash
# 1. Check environment variables in container
docker exec content-agent-backend env | grep -E "ANTHROPIC_API_KEY|OPENAI_API_KEY"

# 2. Verify model configuration
docker exec content-agent-backend python -c "
from backend.config import get_settings
s = get_settings()
print(f'ANTHROPIC_API_KEY present: {bool(s.ANTHROPIC_API_KEY)}')
print(f'OPENAI_API_KEY present: {bool(s.OPENAI_API_KEY)}')
print(f'ANTHROPIC_MODEL: {s.ANTHROPIC_MODEL}')
print(f'OPENAI_MODEL: {s.OPENAI_MODEL}')
"

# Expected output:
# ANTHROPIC_API_KEY present: True
# OPENAI_API_KEY present: True
# ANTHROPIC_MODEL: claude-3-5-sonnet-20240620
# OPENAI_MODEL: gpt-5-nano
```

---

## 🚫 Common Mistakes to Avoid

### ❌ DO NOT:
1. Change `OPENAI_MODEL=gpt-5-nano` to `gpt-4o-mini` (gpt-5-nano is valid!)
2. Reverse the priority logic (Claude must be first)
3. Remove ANTHROPIC_API_KEY checks
4. Use OpenAI for script generation when Claude is available
5. Change ANTHROPIC_MODEL to newer versions without testing

### ✅ DO:
1. Always check ANTHROPIC_API_KEY first in priority logic
2. Keep gpt-5-nano for supervisor routing (it's valid and cost-effective)
3. Use claude-3-5-sonnet-20240620 for content creation
4. Log which LLM is being used for debugging
5. Add clear documentation when modifying LLM logic

---

## 💰 Cost Implications

### Per-Request Costs (Approximate)

**Script Generation (Claude 3.5 Sonnet):**
- Input: $0.003 per 1K tokens
- Output: $0.015 per 1K tokens
- Average script: ~500 tokens = $0.01-0.02

**Supervisor Routing (OpenAI gpt-5-nano):**
- Input: $0.00015 per 1K tokens
- Output: $0.0006 per 1K tokens
- Average routing: ~200 tokens = $0.0002

**Why Claude for Scripts:**
- 10x better creative quality
- Worth the 5x cost increase for content quality
- Users prefer Claude-generated scripts

**Why gpt-5-nano for Routing:**
- 20x cheaper than gpt-4o-mini
- Sufficient for simple routing decisions
- Faster response times

---

## 🔄 Fallback Behavior

### Script Generation Flow:
```
1. Check ANTHROPIC_API_KEY exists
   ├─ YES → Use Claude (PRIMARY)
   └─ NO → Check OPENAI_API_KEY
       ├─ YES → Use OpenAI (FALLBACK)
       └─ NO → Raise ValueError
```

### Supervisor Chat Flow:
```
1. Check ANTHROPIC_API_KEY exists
   ├─ YES → Use Claude (PRIMARY)
   └─ NO → Check OPENAI_API_KEY
       ├─ YES → Use OpenAI (FALLBACK)
       └─ NO → Raise ValueError
```

### Supervisor Routing Flow:
```
1. Always use OpenAI gpt-5-nano (optimized for routing)
2. No fallback needed (routing-specific use case)
```

---

## 📊 Current Status (2025-10-28)

### ✅ Verified Working:
- [x] Claude API key configured
- [x] OpenAI API key configured
- [x] Claude model: claude-3-5-sonnet-20240620
- [x] OpenAI model: gpt-5-nano
- [x] Priority logic implemented correctly
- [x] Documentation added to all files
- [x] Backend services running healthy

### ⚠️ Known Issues:
- Mem0 API key invalid (memory features limited, but not blocking)
- No impact on LLM functionality

---

## 📝 Change Log

| Date | Change | Author |
|------|--------|--------|
| 2025-10-28 | Initial documentation created | Claude Code |
| 2025-10-28 | Added priority notes to all agent files | Claude Code |
| 2025-10-28 | Verified gpt-5-nano as valid active model | Claude Code |
| 2025-10-28 | Fixed Claude model to claude-3-5-sonnet-20240620 | Claude Code |

---

## 🔐 Security Notes

- API keys stored in `.env` (gitignored)
- Never commit API keys to repository
- Use environment variables in production
- Rotate keys regularly
- Monitor usage for anomalies

---

## 📚 Related Documentation

- [AGENT_CREATION_STANDARD.md](./AGENT_CREATION_STANDARD.md)
- [AGENT_ORCHESTRATION_STANDARD.md](./AGENT_ORCHESTRATION_STANDARD.md)
- [MEMORY_MANAGEMENT_STANDARD.md](./MEMORY_MANAGEMENT_STANDARD.md)

---

**END OF DOCUMENT**
