# Agent Contracts Directory

This directory contains JSONContract1st specification files for all agents in the Ybryx Capital multi-agent system.

## Overview

Each JSON file represents a complete agent contract following the JSONContract1st standard, defining:
- Agent identity and version
- LLM model configuration
- Role and responsibilities
- Personality and communication style
- Available tools and capabilities
- Input/output schemas
- Performance metrics
- Escalation rules
- Guardrails and safety measures

## Contract Files

### Level 1: Sales Agent
**File:** `level1_sales_alex.json`
**Agent ID:** `sales_agent_alex`
**Model:** GPT-5-nano (OpenAI)
**Purpose:** Front-line sales engagement on landing page

### Level 2: Equipment Matching Agent
**File:** `level2_equipment_morgan.json`
**Agent ID:** `equipment_matching_agent_morgan`
**Model:** Claude 3.5 Sonnet (Anthropic)
**Purpose:** Post-approval equipment matching and dealer coordination

### Financing Specialist Agent
**File:** `financing_specialist.json`
**Agent ID:** `financing_specialist`
**Model:** Claude 3.5 Sonnet (Anthropic)
**Purpose:** Prequalification analysis, risk scoring, and approval decisions

### Dealer Matching Specialist Agent
**File:** `dealer_matching.json`
**Agent ID:** `dealer_matching_specialist`
**Model:** Claude 3.5 Sonnet (Anthropic)
**Purpose:** Geographic dealer search and matching

### Knowledge Specialist Agent
**File:** `knowledge_specialist.json`
**Agent ID:** `knowledge_specialist`
**Model:** Claude 3.5 Sonnet (Anthropic)
**Purpose:** Equipment information and general questions

### Supervisor Agent
**File:** `supervisor.json`
**Agent ID:** `supervisor`
**Model:** GPT-5-nano (OpenAI)
**Purpose:** Backend orchestration and routing

## Contract Schema

All contracts follow this structure:

```json
{
  "agent_id": "unique_agent_identifier",
  "version": "semantic_version",
  "name": "Human-readable agent name",
  "description": "Agent purpose and responsibilities",
  "model": {
    "provider": "openai | anthropic",
    "model_name": "specific_model",
    "temperature": 0.0-1.0,
    "max_tokens": 100-4096,
    "timeout": 20-60
  },
  "role": "role_classification",
  "personality": {
    "traits": ["array", "of", "traits"],
    "tone": "communication tone",
    "communication_style": "style description"
  },
  "responsibilities": ["array", "of", "responsibilities"],
  "knowledge_base": {
    "topics": [],
    "expertise_areas": []
  },
  "guardrails": {
    "must_not": [],
    "must_always": [],
    "escalate_when": []
  },
  "required_tools": [],
  "optional_tools": [],
  "tools": [],
  "input_schema": {},
  "output_schema": {},
  "performance_metrics": {},
  "escalation_rules": {},
  "memory": {},
  "metadata": {}
}
```

## Usage

### Loading Contracts

```python
import json
from pathlib import Path

def load_agent_contract(agent_id: str) -> dict:
    """Load agent contract by ID."""
    contract_files = {
        "sales_agent_alex": "level1_sales_alex.json",
        "equipment_matching_agent_morgan": "level2_equipment_morgan.json",
        "financing_specialist": "financing_specialist.json",
        "dealer_matching_specialist": "dealer_matching.json",
        "knowledge_specialist": "knowledge_specialist.json",
        "supervisor": "supervisor.json"
    }

    file_path = Path(__file__).parent / contract_files[agent_id]
    with open(file_path, 'r') as f:
        return json.load(f)
```

### Validating Contracts

```python
from pydantic import BaseModel, Field

class AgentContract(BaseModel):
    """Agent contract validation model."""
    agent_id: str
    version: str
    name: str
    description: str
    model: dict
    role: str
    # ... (full schema in app/models/agent_contract.py)

# Validate contract
contract_data = load_agent_contract("sales_agent_alex")
contract = AgentContract(**contract_data)
```

### Version Tracking

Contracts are versioned using semantic versioning (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes to agent behavior or contract structure
- **MINOR**: New features or capabilities added
- **PATCH**: Bug fixes or minor improvements

Contract versions are tracked in the `agent_versions` database table:

```python
from app.database.models import AgentVersion

# Store contract version
agent_version = AgentVersion(
    agent_id="sales_agent_alex",
    version="1.0.0",
    contract_schema=contract_data,
    is_active=True
)
```

## Tool Definitions

Tools are defined within contracts with this structure:

```json
{
  "name": "tool_name",
  "description": "What the tool does",
  "parameters": [
    {
      "name": "param_name",
      "type": "string | number | object | array",
      "description": "Parameter description",
      "required": true,
      "default": "optional_default_value"
    }
  ],
  "returns": "Description of return value"
}
```

## Performance Metrics

Each contract defines target performance metrics:

```json
{
  "performance_metrics": {
    "response_time_target_ms": 2000,
    "accuracy_target": 0.95,
    "success_rate_target": 0.90,
    "customer_satisfaction_target": 4.5
  }
}
```

These metrics are tracked and monitored in production.

## Escalation Rules

Contracts define when to escalate to humans or other agents:

```json
{
  "escalation_rules": {
    "escalate_to_human": [
      "condition_requiring_human",
      "another_condition"
    ],
    "escalate_to_agent_x": [
      "condition_for_agent_transfer"
    ]
  }
}
```

## Guardrails

Safety measures to ensure proper agent behavior:

```json
{
  "guardrails": {
    "must_not": [
      "Never make financial guarantees",
      "Never request sensitive data"
    ],
    "must_always": [
      "Always verify data completeness",
      "Always provide clear next steps"
    ],
    "escalate_when": [
      "Customer explicitly requests human",
      "Technical issue prevents resolution"
    ]
  }
}
```

## Contract Lifecycle

1. **Development**: Create/modify contract JSON file
2. **Validation**: Validate against Pydantic schema
3. **Testing**: Test agent with new contract in sandbox
4. **Staging**: Deploy to staging environment
5. **Production**: Deploy to production with version tracking
6. **Monitoring**: Track performance metrics
7. **Iteration**: Update based on performance data

## Related Documentation

- **Agent Position Outline**: `docs/AGENT_POSITION_OUTLINE.md`
- **Agent Implementation**: `backend/app/graph/agents.py`
- **Supervisor Implementation**: `backend/app/graph/supervisor.py`
- **Contract Models**: `backend/app/models/agent_contract.py`
- **Database Models**: `backend/app/database/models.py`

## Best Practices

1. **Version Every Change**: Always increment version for any contract modification
2. **Test Thoroughly**: Test agent behavior with new contracts before production
3. **Document Changes**: Add notes in metadata about what changed and why
4. **Track Performance**: Monitor metrics before and after contract changes
5. **Backward Compatibility**: Ensure contract changes don't break existing integrations
6. **Clear Descriptions**: Write clear, specific descriptions for all fields
7. **Realistic Targets**: Set achievable performance targets based on data
8. **Safety First**: Always include comprehensive guardrails

## Contributing

When modifying agent contracts:

1. Create a new version (don't modify existing)
2. Update the `version` field following semantic versioning
3. Document changes in `metadata.change_notes`
4. Update implementation code if contract changes behavior
5. Update tests to reflect contract changes
6. Update this README if adding new agents

## Support

For questions about agent contracts:
- Technical: engineering@ybryx.com
- Product: product@ybryx.com
- Documentation: See `docs/AGENT_POSITION_OUTLINE.md`
