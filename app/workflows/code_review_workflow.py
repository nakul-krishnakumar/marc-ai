import shutil

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.auditor_agent import AuditorAgent
from app.agents.style_agent import StyleAgent
from app.workflows.state import RepoAnalysisState


def auditor_agent(state: RepoAnalysisState):
    """
    Analyzes repository structure and prepares for detailed analysis.
    """

    print("Supervisor: initializing repo analysis...")
    print("Repo path:", state["repo_path"])
    repo_path = state["repo_path"]

    auditor = AuditorAgent(repo_path)
    files = auditor.generate_dir_metadata(log_all=False)
    state["files"] = files

    return state


def style_agent(state: RepoAnalysisState):
    print("Style Agent: running Ruff/ESLint linting.")

    styler = StyleAgent()
    result = styler.run(state["repo_path"])

    for i in result.get("findings", []):
        print("tool: ", i.get("tool"))
        print("output: ", i.get("output"))
        print("errors: ", i.get("errors"))
        print("-----\n")
    return {"style_findings": result.get("findings", [])}


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
    # markdown = "\n".join(f"- {f['msg']}" for f in state["merged_findings"])  # type: ignore

    print("tmdir: ", state["repo_path"])
    shutil.rmtree(state["repo_path"], ignore_errors=True)
    # return {"markdown_report": f"### Code Review Report\n{markdown}"}


def build_workflow() -> CompiledStateGraph:
    """
    Build and return the code review workflow graph.
    """
    workflow = StateGraph(RepoAnalysisState)

    workflow.add_node("auditor", auditor_agent)
    workflow.add_node("style", style_agent)
    workflow.add_node("security", security_agent)
    workflow.add_node("performance", performance_agent)
    workflow.add_node("resolver", conflict_resolver)
    workflow.add_node("explainer", explainer_agent)

    workflow.set_entry_point("auditor")
    workflow.add_edge("auditor", "style")
    workflow.add_edge("auditor", "security")
    workflow.add_edge("auditor", "performance")
    workflow.add_edge("style", "resolver")
    workflow.add_edge("security", "resolver")
    workflow.add_edge("performance", "resolver")
    workflow.add_edge("resolver", "explainer")
    workflow.add_edge("explainer", END)

    return workflow.compile()
