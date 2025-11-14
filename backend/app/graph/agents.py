"""Specialist agent implementations."""

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.prebuilt import ToolNode
import structlog

from app.config import settings
from app.graph.state import AgentState
from app.tools import (
    FinancialScoringTool,
    RiskRulesTool,
    DealerLookupTool,
    RobotCatalogTool,
    NotificationTool,
)
from app.memory.manager import MemoryManager

logger = structlog.get_logger()


# Financing Agent
FINANCING_AGENT_PROMPT = """You are a financing specialist for Ybryx Capital's robotics leasing platform.

Your role is to:
1. Analyze prequalification applications
2. Calculate financial scores using the financial_scoring tool
3. Validate compliance using risk_rules_validator
4. Determine lease eligibility and terms
5. Provide clear explanations of decisions

When processing applications:
- Extract business financials (revenue, age, credit rating, industry)
- Run financial scoring to get risk assessment
- Apply compliance rules
- Calculate preliminary lease terms
- Provide personalized recommendations

Be professional, clear, and empathetic. Explain decisions in business terms.

Available tools:
- financial_scoring: Calculate financial scores
- risk_rules_validator: Check compliance rules
- send_notification: Notify applicants of decisions
"""


def create_financing_node() -> callable:
    """Create financing agent node.

    Returns:
        callable: Financing agent function
    """
    # Use Claude for primary reasoning
    llm = ChatAnthropic(
        model=settings.anthropic_primary_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    # Bind tools
    tools = [FinancialScoringTool(), RiskRulesTool(), NotificationTool()]
    llm_with_tools = llm.bind_tools(tools)

    # Initialize memory
    memory_manager = MemoryManager(namespace="agent:financing", composite_scoring=True)

    def financing_node(state: AgentState) -> AgentState:
        """Process financing/prequalification requests.

        Args:
            state: Current state

        Returns:
            AgentState: Updated state
        """
        messages = state["messages"]

        logger.info(
            "financing_agent_invoked",
            application_id=state.get("application_id"),
            message_count=len(messages),
        )

        try:
            # Retrieve relevant memories
            if messages:
                last_message = messages[-1]
                memories = []  # await memory_manager.search(last_message.get("content", ""), limit=3)
                memory_context = memories if memories else []
            else:
                memory_context = []

            # Invoke LLM with tools
            response = llm_with_tools.invoke(
                [SystemMessage(content=FINANCING_AGENT_PROMPT)] + messages
            )

            # Add agent response to messages
            new_messages = [response]

            # Store interaction in memory
            # await memory_manager.add(
            #     content=f"User: {messages[-1].content if messages else ''} | Agent: {response.content}",
            #     metadata={"agent": "financing", "application_id": state.get("application_id")}
            # )

            logger.info(
                "financing_agent_completed",
                application_id=state.get("application_id"),
            )

            return {
                **state,
                "messages": state["messages"] + new_messages,
                "current_agent": "financing",
                "memory_context": memory_context,
            }

        except Exception as e:
            logger.error(
                "financing_agent_error",
                error=str(e),
                application_id=state.get("application_id"),
            )
            return {
                **state,
                "error": f"Financing agent error: {str(e)}",
            }

    return financing_node


# Dealer Matching Agent
DEALER_MATCHING_PROMPT = """You are a dealer matching specialist for Ybryx Capital.

Your role is to:
1. Find authorized dealers based on location and equipment needs
2. Match customers with the best dealers for their requirements
3. Provide dealer contact information and next steps
4. Coordinate dealer notifications for new leads

When matching dealers:
- Use dealer_lookup tool with customer's ZIP code
- Filter by equipment specialties if specified
- Rank by distance and relevance
- Provide clear contact instructions
- Offer to notify dealers on behalf of customer

Be helpful and ensure customers have clear next steps.

Available tools:
- dealer_lookup: Find dealers by location
- notify_dealer: Send lead to dealer
- send_notification: Notify customer
"""


def create_dealer_matching_node() -> callable:
    """Create dealer matching agent node.

    Returns:
        callable: Dealer matching agent function
    """
    llm = ChatAnthropic(
        model=settings.anthropic_primary_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    tools = [DealerLookupTool(), NotificationTool()]
    llm_with_tools = llm.bind_tools(tools)

    memory_manager = MemoryManager(namespace="agent:dealer_matching", composite_scoring=True)

    def dealer_matching_node(state: AgentState) -> AgentState:
        """Process dealer matching requests.

        Args:
            state: Current state

        Returns:
            AgentState: Updated state
        """
        messages = state["messages"]

        logger.info(
            "dealer_matching_agent_invoked",
            application_id=state.get("application_id"),
        )

        try:
            response = llm_with_tools.invoke(
                [SystemMessage(content=DEALER_MATCHING_PROMPT)] + messages
            )

            new_messages = [response]

            logger.info(
                "dealer_matching_agent_completed",
                application_id=state.get("application_id"),
            )

            return {
                **state,
                "messages": state["messages"] + new_messages,
                "current_agent": "dealer_matching",
            }

        except Exception as e:
            logger.error(
                "dealer_matching_agent_error",
                error=str(e),
                application_id=state.get("application_id"),
            )
            return {
                **state,
                "error": f"Dealer matching agent error: {str(e)}",
            }

    return dealer_matching_node


# Knowledge Agent
KNOWLEDGE_AGENT_PROMPT = """You are a knowledge specialist for Ybryx Capital's robotics leasing platform.

Your role is to:
1. Answer questions about robot specifications and capabilities
2. Explain industry use cases and benefits
3. Provide equipment recommendations based on needs
4. Share leasing advantages and process information

When helping customers:
- Use robot_catalog_search to find equipment
- Explain technical specs in business terms
- Highlight ROI and productivity benefits
- Suggest appropriate equipment for their industry

Be informative, consultative, and focus on value.

Available tools:
- robot_catalog_search: Search equipment catalog
"""


def create_knowledge_node() -> callable:
    """Create knowledge agent node.

    Returns:
        callable: Knowledge agent function
    """
    llm = ChatAnthropic(
        model=settings.anthropic_primary_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
    )

    tools = [RobotCatalogTool()]
    llm_with_tools = llm.bind_tools(tools)

    memory_manager = MemoryManager(namespace="agent:knowledge", composite_scoring=True)

    def knowledge_node(state: AgentState) -> AgentState:
        """Process knowledge and information requests.

        Args:
            state: Current state

        Returns:
            AgentState: Updated state
        """
        messages = state["messages"]

        logger.info(
            "knowledge_agent_invoked",
            application_id=state.get("application_id"),
        )

        try:
            response = llm_with_tools.invoke(
                [SystemMessage(content=KNOWLEDGE_AGENT_PROMPT)] + messages
            )

            new_messages = [response]

            logger.info(
                "knowledge_agent_completed",
                application_id=state.get("application_id"),
            )

            return {
                **state,
                "messages": state["messages"] + new_messages,
                "current_agent": "knowledge",
            }

        except Exception as e:
            logger.error(
                "knowledge_agent_error",
                error=str(e),
                application_id=state.get("application_id"),
            )
            return {
                **state,
                "error": f"Knowledge agent error: {str(e)}",
            }

    return knowledge_node


# Sales Agent (Level 1 - Landing Page Guide)
SALES_AGENT_PROMPT = """You are Alex, a friendly Level 1 Sales Agent for Ybryx Capital's robotics equipment leasing platform.

Your role is to welcome prospects, guide them through the website, and help them start their prequalification journey.

**Your Personality:**
- Warm, professional, and consultative
- Focus on understanding their business needs first
- Never pushy, always helpful
- Use clear, jargon-free language

**What You Can Help With:**
1. **Site Navigation:** Guide prospects to relevant pages (Equipment, Industries, Dealers, Prequalify)
2. **Business Understanding:** Learn about their business, industry, and automation needs
3. **Prequalification:** Walk them through the simple prequalification process
4. **Equipment Info:** Show them robots for their specific industry (warehouse, agriculture, manufacturing)
5. **Leasing Benefits:** Explain no upfront capital, flexible terms, tax advantages
6. **Next Steps:** Clear CTAs to start prequalification or browse equipment

**Conversation Flow (Natural, not scripted):**
1. Warm greeting: "Hi! I'm Alex from Ybryx Capital. I help businesses access robotics equipment without the upfront capital burden."
2. Discover needs: Ask about their industry, current challenges, what brought them here
3. Guide appropriately:
   - If interested in specific equipment → Browse catalog
   - If ready to explore financing → Start prequalification
   - If researching → Explain leasing benefits and success stories
4. Handle objections with empathy and facts
5. Always end with a clear next step

**Key Value Props to Emphasize:**
- No upfront capital required
- Prequalify in minutes with soft credit pull
- Flexible lease terms (24-60 months)
- Equipment pays for itself through labor savings
- 1,200+ businesses already leasing with us

**When They're Ready:**
Guide them to /prequalify with: "I can help you see what you qualify for in about 2 minutes. It won't impact your credit score. Shall we get started?"

**Available Tools:**
- robot_catalog_search: Find equipment by industry or category
- send_notification: Send them information or follow-up

Be conversational, ask questions, and focus on helping them succeed. You're a trusted advisor, not a salesperson.
"""


def create_sales_agent_node() -> callable:
    """Create sales agent node for landing page chat.

    Uses GPT-5-nano for fast, conversational interactions.

    Returns:
        callable: Sales agent function
    """
    # Use GPT-5-nano for Level 1 sales conversations (fast, efficient)
    llm = ChatOpenAI(
        model=settings.openai_supervisor_model,  # gpt-5-nano
        temperature=0.7,  # Slightly higher for more conversational tone
        max_completion_tokens=2000,  # GPT-5 requires max_completion_tokens (not max_tokens)
        reasoning_effort="minimal",  # Optimizes GPT-5 for speed/chat (reduces reasoning overhead)
        api_key=settings.openai_api_key,
    )

    tools = [RobotCatalogTool(), NotificationTool()]
    llm_with_tools = llm.bind_tools(tools)

    memory_manager = MemoryManager(namespace="agent:sales", composite_scoring=True)

    def sales_agent_node(state: AgentState) -> AgentState:
        """Process sales/landing page chat requests.

        Args:
            state: Current state

        Returns:
            AgentState: Updated state
        """
        messages = state["messages"]

        logger.info(
            "sales_agent_invoked",
            session_id=state.get("session_id"),
            message_count=len(messages),
        )

        try:
            # Invoke LLM with sales prompt
            response = llm_with_tools.invoke(
                [SystemMessage(content=SALES_AGENT_PROMPT)] + messages
            )

            new_messages = [response]

            logger.info(
                "sales_agent_completed",
                session_id=state.get("session_id"),
                response_length=len(response.content) if hasattr(response, 'content') else 0,
            )

            return {
                **state,
                "messages": state["messages"] + new_messages,
                "current_agent": "sales",
            }

        except Exception as e:
            logger.error(
                "sales_agent_error",
                error=str(e),
                session_id=state.get("session_id"),
            )
            return {
                **state,
                "error": f"Sales agent error: {str(e)}",
            }

    return sales_agent_node
