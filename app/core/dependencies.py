# app/core/dependencies.py
from app.core.config import settings

def get_orchestrator():
    """
    Return an orchestrator / LangGraph client instance.
    This is a factory placeholder — do not initialize heavy clients at import time.
    """
    class DummyOrch:
        def enqueue(self, *args, **kwargs): ...
    return DummyOrch()
