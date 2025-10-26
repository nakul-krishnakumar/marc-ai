from langgraph.graph import END, StateGraph

from app.workflows.state import RepoAnalysisState


# --- Node functions (stubs for now) ---
def supervisor(state: RepoAnalysisState):
    print("Supervisor: initializing repo analysis.")
    return {"python_files": [], "js_files": []}


def style_agent(state: RepoAnalysisState):
    print("Style Agent: running Ruff/ESLint linting.")
    return {"style_findings": [{"msg": "Demo style warning"}]}


def security_agent(state: RepoAnalysisState):
    print("Security Agent: running Bandit/Semgrep.")
    return {"security_findings": [{"msg": "Demo security issue"}]}


def performance_agent(state: RepoAnalysisState):
    print("Performance Agent: running Radon.")
    return {"performance_findings": [{"msg": "Demo performance comment"}]}


def conflict_resolver(state: RepoAnalysisState):
    print("Conflict Resolver: merging agent results.")
    merged = (
        state.get("style_findings", [])
        + state.get("security_findings", [])
        + state.get("performance_findings", [])
    )
    return {"merged_findings": merged}


def explainer_agent(state: RepoAnalysisState):
    print("Explainer Agent: summarizing report.")
    markdown = "\n".join(f"- {f['msg']}" for f in state["merged_findings"])
    return {"markdown_report": f"### Code Review Report\n{markdown}"}


# --- Build the Graph ---
workflow = StateGraph(RepoAnalysisState)

workflow.add_node("supervisor", supervisor)
workflow.add_node("style", style_agent)
workflow.add_node("security", security_agent)
workflow.add_node("performance", performance_agent)
workflow.add_node("resolver", conflict_resolver)
workflow.add_node("explainer", explainer_agent)

# define flow
workflow.set_entry_point("supervisor")
workflow.add_edge("supervisor", "style")
workflow.add_edge("supervisor", "security")
workflow.add_edge("supervisor", "performance")
workflow.add_edge("style", "resolver")
workflow.add_edge("security", "resolver")
workflow.add_edge("performance", "resolver")
workflow.add_edge("resolver", "explainer")
workflow.add_edge("explainer", END)

graph = workflow.compile()
