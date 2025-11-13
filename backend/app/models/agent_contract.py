"""Agent contract models following Dev Standard specification."""

from typing import Any, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ToolParameter(BaseModel):
    """Tool parameter specification."""

    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolSchema(BaseModel):
    """Tool definition for agent capabilities."""

    name: str
    description: str
    parameters: list[ToolParameter]
    returns: str


class MemoryConfig(BaseModel):
    """Memory configuration for agent."""

    enabled: bool = True
    namespace: str
    retention_days: Optional[int] = None
    composite_scoring: bool = True


class PromptTemplate(BaseModel):
    """Prompt template structure."""

    system: str
    user_template: str
    few_shot_examples: Optional[list[dict[str, str]]] = None


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: Literal["openai", "anthropic", "cohere"]
    model: str
    temperature: float = Field(ge=0.0, le=2.0, default=0.7)
    max_tokens: int = Field(gt=0, default=4096)
    timeout: int = Field(gt=0, default=60)


class ComplianceRule(BaseModel):
    """Compliance rule specification."""

    rule_id: str
    description: str
    validator_function: str  # Function name to call
    required: bool = True


class AgentContract(BaseModel):
    """Complete agent contract specification.

    Follows the Dev Standard agent contract format.
    """

    # Identity
    agent_id: str
    version: str
    name: str
    description: str

    # Configuration
    llm_config: LLMConfig
    memory_config: MemoryConfig
    prompts: PromptTemplate

    # Capabilities
    tools: list[ToolSchema]
    capabilities: list[str]

    # Behavior
    max_iterations: int = Field(gt=0, default=10)
    streaming_enabled: bool = True
    error_recovery: bool = True

    # Compliance
    compliance_rules: Optional[list[ComplianceRule]] = None

    # Routing
    upstream_agents: Optional[list[str]] = None  # Can delegate to these agents
    trigger_conditions: Optional[dict[str, Any]] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[dict[str, Any]] = None


class AgentState(BaseModel):
    """State model for agent execution."""

    messages: list[dict[str, Any]] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    current_agent: Optional[str] = None
    memory_context: Optional[list[dict[str, Any]]] = None
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    error: Optional[str] = None
    iteration_count: int = 0
    completed: bool = False


class AgentResponse(BaseModel):
    """Standardized agent response."""

    agent_id: str
    message: str
    state: AgentState
    suggested_actions: Optional[list[dict[str, Any]]] = None
    metadata: Optional[dict[str, Any]] = None
