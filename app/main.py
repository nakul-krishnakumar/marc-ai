# app/main.py
from fastapi import FastAPI

from app.core.config import settings
from app.routers import code_review
from app.workflows.code_review import graph

app = FastAPI(
    title="MARC-AI Multi-Agent Code Review",
    version="1.0.0",
    description="API for reviewing entire codebase",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    redirect_slashes=False,
)

app.include_router(code_review.router, prefix="/api/v1/review", tags=["Review"])

@app.get("/health", tags=["Health"])
async def health_check():
    return { "status": "ok" }

@app.get("/", tags=["Root"])
async def root():
    return { "message": "Welcome to the MARC-AI Multi-Agent Code Review API" }

init_state = {"repo_path": "./demo_repo"}
result = graph.invoke(init_state)
print("\nFinal State:\n", result["markdown_report"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.ENVIRONMENT == "development",
    )

