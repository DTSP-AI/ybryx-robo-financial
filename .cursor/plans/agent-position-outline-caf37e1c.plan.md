<!-- caf37e1c-26e1-47d3-82d9-14e2b3bf5d6d 90fb2076-e77d-4c27-a542-f33a76439fd4 -->
# Agent Position Outline

## Document Structure

Create a comprehensive outline document (`docs/AGENT_POSITION_OUTLINE.md`) that defines:

1. **Level 1 Sales Agent (Alex)** - Initial customer engagement and prequalification data collection
2. **Level 2 Agent** - Post-approval communication and equipment matching
3. **Supervisor Agent** - Backend orchestration, deal management, and human team coordination

Each section will include:

- Agent identity and role description
- Primary responsibilities
- Knowledge base requirements
- Required data capture fields
- Interaction boundaries and handoff points
- Tools and capabilities

## Implementation Details

### File to Create

- `docs/AGENT_POSITION_OUTLINE.md` - Comprehensive agent position specification

### Content Structure

#### Level 1 Sales Agent (Alex)

- **Role**: Front-line sales/service representative
- **Responsibilities**:
- Welcome and guide prospects through website
- Gather initial prequalification data through conversational flow
- Answer general questions about lease terms and robotics industry
- Qualify leads and identify equipment needs
- Guide prospects to prequalification form
- **Knowledge Base**:
- Basic lease terms and financing options
- Robotics industry overview (warehouse, agriculture, manufacturing, etc.)
- Equipment categories and general capabilities
- Prequalification process and requirements
- **Data Capture**:
- Business information (name, type, industry)
- Contact information (email, phone)
- Equipment interests (categories, use cases)
- Initial qualification (revenue range, business age, credit awareness)
- Consent and preferences

#### Level 2 Agent

- **Role**: Post-approval relationship manager
- **Responsibilities**:
- Communicate approved financing amounts and terms
- Match clients with specific equipment based on approval and needs
- Coordinate with dealers for equipment sourcing
- Provide detailed equipment recommendations
- Facilitate next steps in lease process
- **Knowledge Base**:
- Approved financing terms and limits
- Complete equipment catalog with specifications
- Dealer network and capabilities
- Equipment-to-industry matching logic
- Lease term calculations and payment structures
- **Data Capture**:
- Approved amount confirmation
- Equipment selection preferences
- Dealer location and contact preferences
- Timeline and urgency requirements
- Additional business context for equipment matching

#### Supervisor Agent

- **Role**: Backend orchestration and deal management
- **Responsibilities**:
- Provide deal status and application tracking
- Manage workflow between Level 1 and Level 2 agents
- Coordinate with human underwriters for approvals
- Monitor agent performance and handoffs
- Generate reports and analytics for human team
- Escalate complex cases to human team
- **Knowledge Base**:
- All application statuses and workflows
- Underwriter requirements and approval criteria
- Agent performance metrics
- Deal pipeline and conversion data
- Escalation rules and thresholds
- **Data Capture**:
- Application status changes
- Agent handoff events
- Underwriter decisions and notes
- Escalation reasons and resolutions
- Performance metrics and KPIs

### Data Mapping

- Map existing `PrequalificationCreate` schema fields to Level 1 data capture
- Define Level 2 data requirements beyond prequalification
- Define Supervisor tracking and management data

### Integration Points

- Reference existing agent implementations in `backend/app/graph/agents.py`
- Align with existing tools (FinancialScoringTool, DealerLookupTool, RobotCatalogTool)
- Map to existing database models in `backend/app/database/models.py`
- Reference supervisor routing logic in `backend/app/graph/supervisor.py`

## Deliverables

1. Complete outline document with all three agent positions
2. Data capture field specifications
3. Knowledge base requirements per agent
4. Handoff and workflow definitions
5. Integration notes with existing codebase

### To-dos

- [ ] Review existing agent implementations, schemas, and tools to understand current structure
- [ ] Define Level 1 (Alex) agent position: role, knowledge base, data capture requirements
- [ ] Define Level 2 agent position: role, knowledge base, data capture requirements
- [ ] Define Supervisor agent position: role, knowledge base, management capabilities
- [ ] Create comprehensive AGENT_POSITION_OUTLINE.md document with all specifications