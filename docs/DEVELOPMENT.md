

# Development Guide

## Local Development Setup

### Backend Development

#### Initial Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies with dev tools
pip install -r requirements.txt
pip install -e ".[dev]"

# Set up pre-commit hooks (if using)
pre-commit install
```

#### Database Setup
```bash
# Start PostgreSQL (if not using Docker)
# Or use Docker Compose just for database:
docker-compose up -d postgres

# Create initial migration
alembic revision --autogenerate -m "initial schema"

# Apply migrations
alembic upgrade head
```

#### Running the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --log-level debug

# Or using Python directly
python -m app.main
```

#### Code Quality
```bash
# Format code
black app/ tests/
ruff --fix app/ tests/

# Type checking
mypy app/

# Run tests
pytest -v
pytest --cov=app --cov-report=html
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint and format
npm run lint
npm run format
```

## Agent Development

### Creating a New Agent

1. **Define Agent Contract** (`app/models/agent_contract.py`)
```python
new_agent_contract = AgentContract(
    agent_id="my_new_agent",
    version="1.0.0",
    name="My New Agent",
    description="Does something specific",
    llm_config=LLMConfig(...),
    memory_config=MemoryConfig(...),
    tools=[...],
    # ...
)
```

2. **Implement Agent Node** (`app/graph/agents.py`)
```python
def create_my_new_agent_node() -> callable:
    llm = ChatAnthropic(...)
    tools = [MyTool(), AnotherTool()]
    llm_with_tools = llm.bind_tools(tools)

    def my_agent_node(state: AgentState) -> AgentState:
        # Agent logic here
        return updated_state

    return my_agent_node
```

3. **Add to Supervisor** (`app/graph/supervisor.py`)
```python
members = ["financing", "dealer_matching", "knowledge", "my_new_agent", "FINISH"]

# Add node to workflow
workflow.add_node("my_new_agent", create_my_new_agent_node())

# Add routing
workflow.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {
        # ...existing routes
        "my_new_agent": "my_new_agent",
    },
)
workflow.add_edge("my_new_agent", "supervisor")
```

### Creating a New Tool

1. **Define Tool Schema**
```python
# In app/tools/my_tool.py
from typing import Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool

class MyToolInput(BaseModel):
    param1: str = Field(description="Description")
    param2: int = Field(default=10)

class MyTool(BaseTool):
    name: str = "my_tool"
    description: str = "What this tool does"
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, param1: str, param2: int = 10) -> dict:
        # Tool logic
        return {"result": "value"}
```

2. **Register Tool**
```python
# In app/tools/__init__.py
from app.tools.my_tool import MyTool

__all__ = [..., "MyTool"]
```

## Database Migrations

### Creating Migrations
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "add new table"

# Create empty migration
alembic revision -m "custom migration"
```

### Applying Migrations
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade by steps
alembic upgrade +1

# Downgrade
alembic downgrade -1

# Show current version
alembic current

# Show history
alembic history
```

### Migration Best Practices
- Always review auto-generated migrations
- Test migrations on dev database first
- Add data migrations in separate script if needed
- Include both upgrade and downgrade paths

## API Development

### Adding New Endpoints

1. **Create Schema** (`app/schemas/`)
```python
class MyResourceCreate(BaseModel):
    name: str
    value: int

class MyResourceResponse(BaseModel):
    id: str
    name: str
    value: int
    created_at: datetime
```

2. **Create Router** (`app/routers/my_resource.py`)
```python
from fastapi import APIRouter, Depends
from app.deps import get_db

router = APIRouter()

@router.post("/my-resources", response_model=dict)
async def create_resource(
    data: MyResourceCreate,
    db: AsyncSession = Depends(get_db),
):
    # Implementation
    return {"success": True, "data": ..., "error": None}
```

3. **Register Router** (`app/main.py`)
```python
from app.routers import my_resource

app.include_router(
    my_resource.router,
    prefix=settings.api_v1_prefix,
    tags=["my-resources"]
)
```

### Response Format
Always use standard response format:
```python
{
    "success": bool,
    "data": {} | [] | null,
    "error": {
        "message": str,
        "code": str
    } | null
}
```

## Testing

### Writing Tests

```python
# tests/test_my_feature.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_my_endpoint(client: AsyncClient):
    response = await client.post(
        "/api/v1/my-resources",
        json={"name": "test", "value": 42}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

### Running Tests
```bash
# All tests
pytest

# Specific test file
pytest tests/test_routers/test_prequalifications.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose output
pytest -v -s

# Stop on first failure
pytest -x
```

## Debugging

### Backend Debugging
```python
# Add breakpoints
import ipdb; ipdb.set_trace()

# Or use IDE debugger with uvicorn
# Launch config for VS Code:
{
    "name": "FastAPI",
    "type": "python",
    "request": "launch",
    "module": "uvicorn",
    "args": ["app.main:app", "--reload"]
}
```

### Viewing Logs
```bash
# Structured logs in development
# Check console output or logs/app.log

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## Troubleshooting

### Common Issues

**Database connection errors**
```bash
# Check if PostgreSQL is running
docker-compose ps
# Verify DATABASE_URL in .env
```

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
# Check PYTHONPATH
```

**Migration conflicts**
```bash
# Check current state
alembic current
# If stuck, manually set version
alembic stamp head
```

**Agent execution errors**
- Check LLM API keys are set
- Verify model names in config
- Check memory namespace setup
- Review tool schemas

## Performance Optimization

### Backend
- Use async database queries
- Implement caching with Redis
- Batch database operations
- Use connection pooling
- Profile with `cProfile` or `py-spy`

### Frontend
- Implement code splitting
- Use Next.js Image optimization
- Enable static generation where possible
- Minimize client-side JavaScript

## Security Checklist

- [ ] Environment variables not committed
- [ ] API keys stored securely
- [ ] Database credentials rotated
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection protection (using ORM)
- [ ] XSS prevention
- [ ] HTTPS in production
- [ ] Secrets management configured
