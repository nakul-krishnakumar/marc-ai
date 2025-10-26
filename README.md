# MARC-AI — Multi-Agent Review & Consolidation

Cloud-native FastAPI application that orchestrates LangGraph agents to run static linters & scanners (Ruff, ESLint, Bandit, Semgrep, Radon) and consolidates findings into explainable markdown reports using Azure OpenAI.

## Features

-   **Multi-agent orchestration** with LangGraph
-   **Static analysis only** — no code execution
-   **Parallel agent execution** for style, security, and performance checks
-   **AI-powered explanations** via Azure OpenAI (GPT-4)
-   **Async REST API** with FastAPI
-   **Containerized** with multi-stage Docker builds

## Quick Start

### Prerequisites

-   Python 3.11+
-   Docker & Docker Compose
-   Node.js & npm (for ESLint)

### Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Copy environment template:

```bash
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

3. Run the application:

```bash
uvicorn app.main:app --reload
```

4. Access API docs at `http://localhost:8000/docs`

### Docker Development

Build and run the development environment:

```bash
# Build and start in foreground
docker-compose -f docker-compose.dev.yml up --build

# Or run in background
docker-compose -f docker-compose.dev.yml up -d --build

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop
docker-compose -f docker-compose.dev.yml down
```

### Docker Production

Build and run the production environment:

```bash
# Build and start in background
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop
docker-compose -f docker-compose.prod.yml down
```

### Build Specific Stage Only

```bash
# Build dev stage
docker build --target dev -t marc-ai:dev .

# Build prod stage
docker build --target prod -t marc-ai:prod .

# Run manually (without docker-compose)
docker run -p 8000:8000 --env-file .env marc-ai:prod
```

## API Endpoints

-   `GET /api/v1/health/` — Health check
-   `POST /api/v1/review/analyze` — Trigger code analysis
-   `GET /api/v1/review/status/{run_id}` — Check analysis status
-   `GET /api/v1/review/report/{run_id}` — Retrieve analysis report

## Project Structure

```
marc-ai/
├── app/
│   ├── agents/          # Analysis agents (style, security, performance)
│   ├── core/            # Config, logging, dependencies
│   ├── models/          # Pydantic schemas
│   ├── routers/         # API endpoints
│   ├── services/        # Business logic
│   ├── utils/           # Utilities (subprocess, parsers)
│   └── workflows/       # LangGraph workflows
├── tests/               # Test suite
├── Dockerfile           # Multi-stage container build
└── requirements.txt     # Python dependencies
```

## Security

-   All static analysis tools run via safe subprocess calls (`shell=False`)
-   Timeouts and resource limits enforced
-   No repository code execution
-   Isolated working directories per analysis run

## Development Status

**Current Phase:** Initialization — scaffolding complete, business logic pending.

See `INIT_PROJECT.md` for detailed architecture and implementation guidance.

## License

MIT
