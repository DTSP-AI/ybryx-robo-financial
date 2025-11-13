# Ybryx Capital - Multi-Agent System Specification

**Version:** 1.0
**Last Updated:** 2025-11-13
**Platform:** Robotics Equipment Financing

---

## System Overview

The Ybryx Capital platform employs a sophisticated multi-agent architecture designed to guide prospects from initial inquiry through equipment financing and dealer matching. The system uses a combination of fast routing agents (GPT-5-nano) for conversational interactions and complex reasoning agents (Claude 3.5 Sonnet) for financial analysis and matching logic.

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                          │
│  Landing Page Chat  │  Prequalify Form  │  Dashboard            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Level 1: Sales Agent "Alex"                  │
│              (GPT-5-nano - Landing Page Engagement)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Prequalification Form Submission              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supervisor Agent                           │
│            (GPT-5-nano - Backend Orchestration)                 │
│                                                                 │
│  Routes to: ┌──────────────┬──────────────┬──────────────┐    │
│            │  Financing   │  Dealer      │  Knowledge   │    │
│            │  Specialist  │  Matching    │  Specialist  │    │
│            └──────────────┴──────────────┴──────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         Level 2: Equipment Matching Agent "Morgan"              │
│         (Claude 3.5 Sonnet - Post-Approval Support)             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Specifications

---

## Level 1: Sales Agent "Alex"

### Identity

**Agent ID:** `sales_agent_alex`
**Version:** 1.0
**Model:** GPT-5-nano (OpenAI)
**Personality:** Warm, consultative, never pushy, professional

### Role & Responsibilities

Alex is the front-line sales agent on the landing page. Primary responsibilities:

1. **Welcome & Discovery**: Greet prospects and understand their business needs
2. **Site Navigation**: Guide prospects to relevant pages (Equipment, Industries, Dealers)
3. **Equipment Exploration**: Help discover appropriate robotics for their industry
4. **Prequalification Guidance**: Walk prospects through the qualification process
5. **Value Communication**: Explain leasing benefits without being salesy

### Conversation Strategy

**Opening**: "Hi! I'm Alex from Ybryx Capital. I help businesses access robotics equipment without the upfront capital burden. What brings you here today?"

**Discovery Questions**:
- What industry are you in?
- What operational challenges are you facing?
- Have you explored automation before?
- What brought you to our site today?

**Value Propositions to Emphasize**:
- No upfront capital required
- Prequalify in minutes with soft credit pull
- Flexible lease terms (24-60 months)
- Equipment pays for itself through labor savings
- 1,200+ businesses already leasing

### Knowledge Base

- **Leasing Basics**: Terms, monthly payments, tax advantages, no upfront cost
- **Robot Categories**: AMRs, AGVs, Drones, Robotic Arms, Cobots
- **Industry Use Cases**: Logistics/warehousing, agriculture, manufacturing, delivery, construction
- **Prequalification Process**: Simple form, soft credit check, instant decision
- **Dealer Network**: 300+ authorized dealers nationwide

### Data Capture

| Field | Type | Purpose |
|-------|------|---------|
| business_name | string | Personalization |
| business_type | enum | LLC, Corporation, Partnership, Sole Proprietor |
| industry | enum | Route to relevant equipment |
| email | string | Follow-up communication |
| phone | string | Optional contact |
| equipment_interests | array | Categories they're exploring |
| revenue_range | string | Pre-qualify context |
| business_age | string | Risk assessment context |
| credit_awareness | string | Self-reported credit understanding |

### Available Tools

#### robot_catalog_search
**Purpose:** Find equipment by industry, category, or use case
**Parameters:**
- `query` (string): Search term
- `category` (string): AMR, AGV, Drone, etc.
- `use_case` (string): Industry filter
- `max_results` (int): Limit results (default: 5)

**Usage Example:**
```python
robot_catalog_search(
    query="warehouse",
    category="AMR",
    use_case="logistics",
    max_results=3
)
```

#### send_notification
**Purpose:** Send follow-up information or reminders
**Parameters:**
- `recipient` (string): Email or phone
- `notification_type` (enum): email, sms, both
- `subject` (string): Notification subject
- `message` (string): Content
- `metadata` (dict): Additional context

**Usage Example:**
```python
send_notification(
    recipient="john@example.com",
    notification_type="email",
    subject="Your Equipment Options",
    message="Here are the robots we discussed..."
)
```

### Handoff Rules

**Trigger:** Customer indicates readiness to prequalify

**Handoff Message:**
"I can help you see what you qualify for in about 2 minutes. It won't impact your credit score. Shall we get started?"

**Redirect:** `/prequalify` form

**State Transfer:**
- Captured data (business_name, email, etc.)
- Equipment interests
- Conversation context

### JSON Contract Schema

**Input Schema:**
```json
{
  "thread_id": "uuid",
  "message": "string",
  "context": {
    "page": "landing",
    "session_id": "uuid",
    "previous_captures": {}
  }
}
```

**Output Schema:**
```json
{
  "agent_id": "sales_agent_alex",
  "response": "string",
  "suggested_actions": [
    {
      "type": "navigate",
      "target": "/prequalify",
      "label": "Start Prequalification"
    }
  ],
  "captured_data": {
    "business_name": "string",
    "industry": "string",
    "equipment_interests": ["string"]
  },
  "handoff_ready": false
}
```

### Performance Metrics

- **Response Time Target:** < 2 seconds
- **Engagement Rate:** % of visitors who interact
- **Conversion to Prequalify:** % who click through
- **Data Capture Completeness:** Fields collected per session
- **Sentiment Score:** Positive interaction detection

### Guardrails

1. **Never** make financial promises or guarantee approval
2. **Never** request sensitive information (SSN, bank accounts)
3. **Always** clarify that prequalification is a soft credit check
4. **Always** be transparent about being an AI assistant
5. **Escalate** complex legal or financial questions to human support

---

## Level 2: Equipment Matching Agent "Morgan"

### Identity

**Agent ID:** `equipment_matching_agent_morgan`
**Version:** 1.0
**Model:** Claude 3.5 Sonnet (Anthropic)
**Personality:** Expert consultant, detail-oriented, helpful, relationship-focused

### Role & Responsibilities

Morgan is the post-approval relationship manager. Responsibilities:

1. **Approval Communication**: Inform customers of their approval and terms
2. **Equipment Matching**: Match approved financing to specific equipment needs
3. **Dealer Coordination**: Find and connect customers with local authorized dealers
4. **Timeline Planning**: Help customers plan deployment schedules
5. **Deal Closure**: Guide customers through final steps

### Activation Trigger

Morgan is activated when a `Prequalification` record status changes to `APPROVED`.

**Trigger Event:**
```python
if prequalification.status == PrequalificationStatus.APPROVED:
    activate_agent("equipment_matching_agent_morgan")
```

### Knowledge Base

- **Full Equipment Catalog**: Detailed specs, pricing, applications
- **Dealer Network**: Coverage areas, specialties, performance ratings
- **Financing Terms**: Approved amounts, rates, term options
- **Industry Best Practices**: Equipment selection for specific use cases
- **ROI Calculations**: Labor savings, productivity gains, payback periods

### Data Capture

| Field | Type | Purpose |
|-------|------|---------|
| approved_amount | float | Maximum financing available |
| equipment_preferences | array | Specific models of interest |
| dealer_location | string | ZIP code for dealer matching |
| timeline | string | When they need equipment |
| current_operations | string | Baseline for ROI calculations |
| deployment_assistance | boolean | Need for installation support |

### Available Tools

#### robot_catalog_search
**Purpose:** Deep equipment search with technical specs
(Same parameters as Level 1, but used for detailed matching)

#### dealer_lookup
**Purpose:** Find authorized dealers by location and specialty
**Parameters:**
- `zip_code` (string): Customer location
- `specialty` (string): Equipment category
- `max_results` (int): Dealers to return

**Usage Example:**
```python
dealer_lookup(
    zip_code="94105",
    specialty="AMRs",
    max_results=3
)
```

#### send_notification
**Purpose:** Send approval letters, dealer matches, next steps
(Same as Level 1)

#### notify_dealer
**Purpose:** Send lead information to matched dealers
**Parameters:**
- `dealer_email` (string): Dealer contact
- `lead_info` (dict): Customer information
- `message_template` (string): Template to use

**Usage Example:**
```python
notify_dealer(
    dealer_email="sales@dealer.com",
    lead_info={
        "business_name": "Acme Corp",
        "approved_amount": 50000,
        "equipment_interest": "Warehouse AMRs"
    },
    message_template="new_lead"
)
```

### Workflow

```
1. Application Approved
   │
   ▼
2. Morgan: Send Approval Notification
   │
   ▼
3. Gather Equipment Preferences
   │
   ▼
4. Search Catalog (robot_catalog_search)
   │
   ▼
5. Present Equipment Options
   │
   ▼
6. Gather Location & Timeline
   │
   ▼
7. Find Dealers (dealer_lookup)
   │
   ▼
8. Present Dealer Matches
   │
   ▼
9. Customer Selects Dealer
   │
   ▼
10. Notify Dealer (notify_dealer)
    │
    ▼
11. Confirm Next Steps
    │
    ▼
12. Close Conversation
```

### Handoff Rules

**Handoff to Human:**
- Customer requests negotiation on terms
- Technical questions beyond catalog specs
- Dealer disputes or issues
- Contract modifications

**Handoff to Support:**
- Payment processing questions
- Account management
- Post-delivery issues

### JSON Contract Schema

**Input Schema:**
```json
{
  "prequalification_id": "uuid",
  "approved_amount": 50000.00,
  "customer_data": {
    "business_name": "string",
    "email": "string",
    "phone": "string",
    "industry": "string"
  },
  "preliminary_terms": {
    "max_amount": 50000.00,
    "term_months": 48,
    "estimated_rate": 8.5
  }
}
```

**Output Schema:**
```json
{
  "agent_id": "equipment_matching_agent_morgan",
  "response": "string",
  "matched_equipment": [
    {
      "robot_id": "uuid",
      "name": "string",
      "monthly_payment": 1299.00
    }
  ],
  "matched_dealers": [
    {
      "dealer_id": "uuid",
      "name": "string",
      "distance_miles": 5.2,
      "phone": "string"
    }
  ],
  "next_steps": ["string"],
  "deal_status": "dealer_matched"
}
```

### Performance Metrics

- **Response Time Target:** < 5 seconds
- **Equipment Match Accuracy:** Customer satisfaction rating
- **Dealer Match Success Rate:** % of customers who contact dealer
- **Deal Closure Rate:** % who complete lease
- **Time to Dealer Match:** Average hours from approval to dealer connection

### Guardrails

1. **Never** exceed approved financing amount
2. **Never** recommend equipment outside customer's industry expertise
3. **Always** disclose dealer relationships and partnerships
4. **Always** confirm customer location before dealer matching
5. **Escalate** if customer disputes approval terms

---

## Level 3: Financing Specialist Agent

### Identity

**Agent ID:** `financing_specialist`
**Version:** 1.0 (existing implementation)
**Model:** Claude 3.5 Sonnet (Anthropic)
**Personality:** Professional, analytical, empathetic, clear communicator

### Role & Responsibilities

The Financing Specialist handles prequalification analysis. Responsibilities:

1. **Application Analysis**: Review submitted prequalification forms
2. **Financial Scoring**: Calculate risk scores using financial_scoring tool
3. **Compliance Validation**: Ensure applications meet regulatory requirements
4. **Lease Term Calculation**: Determine preliminary lease terms
5. **Decision Communication**: Provide clear explanations of approval/decline

### Available Tools

#### financial_scoring
**Purpose:** Calculate financial risk score
**Parameters:**
- `annual_revenue` (string): Revenue range
- `business_age` (string): Years in business
- `credit_rating` (string): Self-reported credit
- `industry` (string): Business industry

#### risk_rules_validator
**Purpose:** Check compliance and risk rules
**Parameters:**
- `application_data` (dict): Full application
- `score` (float): Calculated risk score

#### send_notification
**Purpose:** Send approval/decline notifications

### Current Implementation

Located in: `C:\AI_src\ybryx-robotics-financing\backend\app\graph\agents.py` (lines 24-133)

### Integration Points

- **Input:** Prequalification form submissions
- **Output:** Status update (APPROVED, DECLINED, NEEDS_REVIEW)
- **Database:** Updates `Prequalification` table with results
- **Triggers:** Activates Morgan on approval

---

## Level 4: Dealer Matching Agent

### Identity

**Agent ID:** `dealer_matching_specialist`
**Version:** 1.0 (existing implementation)
**Model:** Claude 3.5 Sonnet (Anthropic)
**Personality:** Helpful, knowledgeable about dealer network, logistics-focused

### Role & Responsibilities

The Dealer Matching Specialist finds dealers. Responsibilities:

1. **Geographic Search**: Find dealers near customer location
2. **Specialty Matching**: Filter by equipment expertise
3. **Ranking**: Rank dealers by distance and relevance
4. **Contact Facilitation**: Provide dealer information and next steps
5. **Lead Notification**: Alert dealers of new opportunities

### Available Tools

#### dealer_lookup
**Purpose:** Search dealer database

#### notify_dealer
**Purpose:** Send lead notifications

#### send_notification
**Purpose:** Send dealer matches to customer

### Current Implementation

Located in: `C:\AI_src\ybryx-robotics-financing\backend\app\graph\agents.py` (lines 136-224)

### Integration Points

- **Input:** Customer location and equipment needs
- **Output:** List of matched dealers with contact info
- **Database:** Queries `Dealer` table
- **Triggers:** Can be called by Morgan or Supervisor

---

## Level 5: Knowledge Specialist Agent

### Identity

**Agent ID:** `knowledge_specialist`
**Version:** 1.0 (existing implementation)
**Model:** Claude 3.5 Sonnet (Anthropic)
**Personality:** Informative, consultative, technical but accessible

### Role & Responsibilities

The Knowledge Specialist answers questions. Responsibilities:

1. **Equipment Information**: Explain robot specs and capabilities
2. **Industry Guidance**: Share use cases and benefits
3. **Equipment Recommendations**: Suggest appropriate equipment
4. **Leasing Education**: Explain leasing advantages and process
5. **ROI Communication**: Highlight productivity and savings benefits

### Available Tools

#### robot_catalog_search
**Purpose:** Search equipment catalog

### Current Implementation

Located in: `C:\AI_src\ybryx-robotics-financing\backend\app\graph\agents.py` (lines 227-312)

### Integration Points

- **Input:** Customer questions about equipment or process
- **Output:** Informative responses with catalog data
- **Database:** Queries `Robot` table
- **Triggers:** Called by Supervisor for informational requests

---

## Supervisor Agent

### Identity

**Agent ID:** `supervisor`
**Version:** 1.0 (existing implementation)
**Model:** GPT-5-nano (OpenAI)
**Purpose:** Backend orchestration and routing

### Role & Responsibilities

The Supervisor routes backend requests to specialist agents. Responsibilities:

1. **Request Analysis**: Understand user intent
2. **Agent Routing**: Delegate to appropriate specialist
3. **State Management**: Track conversation state and iterations
4. **Error Handling**: Manage failures and fallbacks
5. **Completion Detection**: Determine when task is finished

### Routing Logic

**Routes to:**
- `financing` - Prequalification applications, financial questions
- `dealer_matching` - Dealer searches, location-based requests
- `knowledge` - Equipment info, general questions
- `FINISH` - Task complete

**Routing Decision Factors:**
- User message intent
- Current conversation state
- Previous agent
- Iteration count (max 10)

### Current Implementation

Located in: `C:\AI_src\ybryx-robotics-financing\backend\app\graph\supervisor.py`

### Integration Points

- **Input:** User messages and application data
- **Output:** Routing decisions
- **Graph:** Uses LangGraph StateGraph for orchestration
- **Memory:** Uses MemorySaver for conversation persistence

### Workflow

```
User Request
    │
    ▼
Supervisor Analyzes
    │
    ├─→ [financing] → Process → Return to Supervisor
    ├─→ [dealer_matching] → Process → Return to Supervisor
    ├─→ [knowledge] → Process → Return to Supervisor
    └─→ [FINISH] → End
```

---

## Data Mapping to Existing Schemas

### Prequalification Table

Maps to: `backend/app/database/models.py` - `Prequalification` model

| Field | Type | Source |
|-------|------|--------|
| business_name | String | Alex captures, form collects |
| business_type | Enum | Form selection |
| industry | Enum | Alex discovers, form confirms |
| email | String | Alex captures |
| phone | String | Alex or form |
| selected_equipment | JSON | Form multi-select |
| quantity | String | Form input |
| annual_revenue | String | Form selection |
| business_age | String | Form selection |
| credit_rating | String | Form selection |
| consent | Boolean | Form checkbox |
| status | Enum | Set by Financing Agent |
| agent_analysis | JSON | Financing Agent output |
| preliminary_terms | JSON | Financing Agent calculations |

### Robot Table

Maps to: `backend/app/database/models.py` - `Robot` model

Used by: Alex, Morgan, Knowledge Agent

### Dealer Table

Maps to: `backend/app/database/models.py` - `Dealer` model

Used by: Morgan, Dealer Matching Agent

### Thread & ThreadMessage Tables

Maps to: `backend/app/database/models.py` - `Thread`, `ThreadMessage` models

Used by: All agents for conversation persistence

---

## Agent Communication Contracts

### Alex → Prequalification Form

**Data Transfer:**
```json
{
  "captured_data": {
    "business_name": "Acme Corp",
    "industry": "logistics",
    "email": "john@acme.com",
    "equipment_interests": ["AMR", "AGV"]
  },
  "session_id": "uuid",
  "thread_id": "uuid"
}
```

### Prequalification Form → Financing Agent

**Data Transfer:**
```json
{
  "prequalification_id": "uuid",
  "application_data": {
    "business_name": "string",
    "business_type": "llc",
    "industry": "logistics",
    "annual_revenue": "$500k-$1M",
    "business_age": "3-5 years",
    "credit_rating": "good",
    "selected_equipment": ["uuid1", "uuid2"]
  }
}
```

### Financing Agent → Morgan

**Data Transfer:**
```json
{
  "prequalification_id": "uuid",
  "status": "APPROVED",
  "approved_amount": 50000.00,
  "preliminary_terms": {
    "max_amount": 50000.00,
    "term_months": 48,
    "estimated_rate": 8.5,
    "monthly_payment_range": "1200-1500"
  },
  "customer_data": {
    "business_name": "string",
    "email": "string",
    "phone": "string",
    "industry": "logistics"
  }
}
```

---

## Error Handling & Escalation

### Agent Error Scenarios

1. **Tool Failure**
   - Log error details
   - Return graceful error message
   - Retry once
   - Escalate to supervisor if persistent

2. **Database Connection Issues**
   - Use cached data if available
   - Notify user of temporary issue
   - Queue request for retry
   - Escalate to engineering if prolonged

3. **LLM Timeout**
   - Retry with reduced token limit
   - Fallback to simpler model
   - Apologize and offer callback
   - Log for monitoring

4. **Invalid User Input**
   - Request clarification politely
   - Provide examples of valid input
   - Guide to correct format
   - Never expose technical errors

### Escalation Rules

**Escalate to Human Support When:**
- Customer explicitly requests human agent
- Agent unable to resolve after 3 attempts
- Legal or compliance questions
- Contract negotiations
- Dispute resolution
- Technical issues outside agent scope

**Escalation Process:**
```
1. Agent detects escalation condition
2. Log escalation reason
3. Notify customer: "Let me connect you with a specialist"
4. Create support ticket with full context
5. Transfer to human agent queue
6. Send customer confirmation with ticket ID
```

---

## Performance Monitoring

### Key Metrics by Agent

| Agent | Primary KPI | Target |
|-------|------------|--------|
| Alex | Engagement Rate | > 40% |
| Alex | Prequalify Conversion | > 15% |
| Financing | Processing Time | < 30 sec |
| Financing | Approval Rate | 60-70% |
| Morgan | Dealer Match Rate | > 90% |
| Morgan | Deal Closure Rate | > 50% |
| Knowledge | Answer Accuracy | > 95% |
| Supervisor | Routing Accuracy | > 98% |

### System Health Indicators

- **Uptime:** > 99.9%
- **Average Response Time:** < 3 seconds
- **Error Rate:** < 1%
- **Escalation Rate:** < 5%

---

## Security & Compliance

### Data Protection

1. **PII Handling**
   - Encrypt all personal data at rest and in transit
   - Never log SSN, account numbers, or passwords
   - Redact sensitive data in logs and monitoring

2. **Credit Data**
   - Soft credit pulls only for prequalification
   - Comply with FCRA requirements
   - Provide adverse action notices if declined

3. **Authentication**
   - JWT tokens for API access
   - Session management for web interface
   - Rate limiting on API endpoints

### Compliance Requirements

- **GDPR:** Right to deletion, data portability
- **CCPA:** California privacy rights
- **FCRA:** Fair credit reporting practices
- **TILA:** Truth in lending disclosures
- **ADA:** Accessibility standards

---

## Deployment & Versioning

### Agent Version Control

Agents follow semantic versioning: MAJOR.MINOR.PATCH

**Version History Tracking:**
```sql
INSERT INTO agent_versions (agent_id, version, contract_schema, is_active)
VALUES ('sales_agent_alex', '1.0.0', {...}, true);
```

### Deployment Process

1. **Development**: Test in sandbox environment
2. **Staging**: Validate against production data
3. **Canary**: Roll out to 10% of traffic
4. **Full Release**: Deploy to all users
5. **Monitor**: Track metrics for 48 hours
6. **Rollback**: Revert if metrics degrade

### A/B Testing

Test variations of:
- Prompt wording
- Tool selection strategies
- Handoff timing
- Response length

Track impact on conversion and satisfaction metrics.

---

## Future Enhancements

### Roadmap

**Q2 2025:**
- Add Spanish language support
- Implement voice interface
- Enhanced ROI calculator tool

**Q3 2025:**
- Level 3 underwriting agent (complex applications)
- Contract generation agent
- Post-deployment support agent

**Q4 2025:**
- Multi-modal support (image analysis of facilities)
- Predictive maintenance agent
- Fleet optimization agent

---

## Appendix: Technical Reference

### File Locations

- **Agent Implementations:** `backend/app/graph/agents.py`
- **Supervisor:** `backend/app/graph/supervisor.py`
- **State Management:** `backend/app/graph/state.py`
- **Tools:** `backend/app/tools/`
- **Models:** `backend/app/database/models.py`
- **API Endpoints:** `backend/app/api/v1/`

### Environment Configuration

Required environment variables:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_ORG_ID=org-...
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Tool Development Guidelines

When adding new tools:
1. Create tool class extending `BaseTool`
2. Define Pydantic input schema
3. Implement `_run()` method
4. Add error handling and logging
5. Write unit tests
6. Update agent contracts
7. Document in this outline

---

**End of Agent Position Outline**
