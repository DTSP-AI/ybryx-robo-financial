# Ybryx Capital - Robotics Equipment Financing Platform

A full-stack application for robotics equipment leasing and financing, built with Next.js, FastAPI, and LangGraph multi-agent orchestration.

## Project Structure

```
ybryx-robotics-financing/
├── frontend/              # Next.js frontend application
│   ├── app/              # Next.js 14 app directory
│   ├── components/       # React components
│   └── public/           # Static assets
├── backend/              # FastAPI backend with LangGraph agents
│   ├── app/
│   │   ├── agents/       # Specialist agent implementations
│   │   ├── database/     # SQLAlchemy models and migrations
│   │   ├── graph/        # LangGraph workflows & memory nodes
│   │   ├── memory/       # Unified Supabase + Mem0 memory system
│   │   ├── models/       # Pydantic models and contracts
│   │   ├── routers/      # FastAPI endpoints
│   │   ├── schemas/      # Request/response schemas
│   │   ├── services/     # Business logic
│   │   ├── tools/        # LangChain tools
│   │   └── examples/     # Integration examples
│   ├── alembic/          # Database migrations
│   ├── tests/            # Pytest test suite
│   └── supabase_schema.sql  # Supabase database schema
├── docs/                 # Documentation
└── docker-compose.yml    # Docker orchestration
```

## Features

### Frontend
- **Equipment Catalog**: Browse autonomous robots, AMRs, AGVs, drones, and robotic arms
- **Prequalification Flow**: Multi-step application form with soft credit check
- **Dealer Locator**: Find authorized dealers by ZIP code and specialty
- **Industry Showcase**: Use cases and ROI for logistics, agriculture, manufacturing, etc.

### Backend
- **Multi-Agent System**: LangGraph-orchestrated agents for financing, dealer matching, and knowledge
- **Memory Management**: Mem0-backed persistent memory with composite scoring
- **Financial Scoring**: Automated prequalification analysis with compliance rules
- **RESTful API**: OpenAPI-documented endpoints with snake_case JSON

### Agent Architecture
1. **Supervisor Agent**: Routes requests using OpenAI GPT-5-nano
2. **Financing Agent**: Analyzes applications, scores creditworthiness (Claude)
3. **Dealer Matching Agent**: Geospatial lookup and lead routing
4. **Knowledge Agent**: Equipment recommendations and industry insights

### Unified Memory System
- **Supabase (PostgreSQL)**: Structured storage for sessions, executions, audit logs
- **Mem0 (PGVector)**: Vector embeddings for semantic recall and context
- **MemoryManager**: Single authority for all memory operations
- **LangGraph Nodes**: context_loader and memory_writer for seamless integration
- **Standards Compliant**: Follows all Agentic Systems Infrastructure Standards

📚 **See**: [Unified Memory README](docs/UNIFIED_MEMORY_README.md) | [Memory System Architecture](docs/MEMORY_SYSTEM.md)

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd ybryx-robotics-financing
```

2. **Configure environment variables**
```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with your API keys (OpenAI, Anthropic, Supabase, etc.)
```

3. **Start all services**
```bash
docker-compose up -d
```

This starts:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

4. **Deploy Supabase schema**
```bash
# Apply schema to your Supabase project
# Option A: Via Supabase dashboard SQL editor
# Copy contents of backend/supabase_schema.sql and execute

# Option B: Via Supabase CLI
supabase db push < backend/supabase_schema.sql
```

5. **Run backend database migrations** (for non-Supabase tables)
```bash
docker-compose exec backend alembic upgrade head
```

6. **Optional: Start PgAdmin**
```bash
docker-compose --profile tools up -d pgadmin
# Access at http://localhost:5050 (admin@ybryx.local / admin)
```

### Memory System Setup

The unified memory system requires Supabase for structured storage and Mem0 for vector operations:

```bash
# 1. Create Supabase project at https://supabase.com
# 2. Get your project URL and service role key
# 3. Apply schema: backend/supabase_schema.sql
# 4. Sign up for Mem0 at https://mem0.ai
# 5. Configure .env with both keys
# 6. Test connection:

python -c "
from app.memory.unified_manager import get_memory_manager
mm = get_memory_manager()
print(f'Supabase: {mm.supabase is not None}')
print(f'Mem0: {mm.mem0 is not None}')
"
```

📚 **Quick Start**: [Unified Memory README](docs/UNIFIED_MEMORY_README.md)

### Local Development

#### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Key Endpoints

#### Prequalifications
- `POST /prequalifications` - Submit application
- `GET /prequalifications/{id}` - Get application status

#### Robots/Equipment
- `GET /robots` - List equipment (supports search, category, use_case filters)
- `GET /robots/{id}` - Get equipment details

#### Dealers
- `GET /dealers` - List dealers (supports zip_code filter)
- `POST /dealers/match` - Match dealers to requirements

See full API documentation at http://localhost:8000/docs

## Configuration

### Required Environment Variables

```env
# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Supabase (REQUIRED for unified memory)
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=...

# Mem0 (REQUIRED for vector memory)
MEM0_API_KEY=...
MEM0_BACKEND=pgvector

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ybryx

# Optional: Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...

# Optional: Mem0 Memory
MEM0_API_KEY=...
MEM0_HOST=https://api.mem0.ai

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
```

## Testing

### Backend Tests
```bash
cd backend
pytest
# With coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Build

1. **Backend**
```bash
cd backend
docker build -t ybryx-backend:latest --target production .
```

2. **Frontend**
```bash
cd frontend
docker build -t ybryx-frontend:latest .
```

### Environment Considerations
- Set `DEBUG=False` in backend
- Use production database credentials
- Enable HTTPS/TLS
- Configure CORS for production domains
- Set up monitoring and logging
- Use secrets management (AWS Secrets Manager, Azure Key Vault, etc.)

## Architecture Decisions

### LLM Strategy
- **OpenAI GPT-5-nano**: Supervisor routing (low latency, cost-effective)
- **Anthropic Claude 3.5 Sonnet**: Primary reasoning (high quality, complex analysis)

### Memory Management
- **Mem0**: Persistent agent memory with namespace isolation
- **Composite Scoring**: Recency + relevance + frequency for retrieval
- **TTL Policies**: Automatic memory expiration

### Database
- **PostgreSQL**: Primary data store with async SQLAlchemy
- **Alembic**: Schema migrations
- **Redis**: Caching and session management

## Contributing

1. Follow the Dev Standard specifications in `Dev_Standard/`
2. Use structured logging (structlog) for all operations
3. Write tests for new features
4. Update API documentation
5. Follow snake_case for JSON APIs
6. Use Pydantic for data validation

## License

Proprietary - Ybryx Capital

## Support

For issues or questions:
- Email: contact@ybryxcapital.com
- Internal Slack: #ybryx-engineering
