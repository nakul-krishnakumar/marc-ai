import shutil

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.auditor_agent import AuditorAgent
from app.agents.security_agent import SecurityAgent
from app.agents.style_agent import StyleAgent
from app.core.logger import logger
from app.workflows.state import RepoAnalysisState


def auditor_agent(state: RepoAnalysisState):
    """
    Analyzes repository structure and prepares for detailed analysis.
    """

    logger.info("Auditor: initializing repo analysis...")
    logger.info(f"Repo path: {state['repo_path']}")
    repo_path = state["repo_path"]

    auditor = AuditorAgent(repo_path)
    files = auditor.generate_dir_metadata(log_all=state['log_all_audits'])
    state["files"] = files

    return state


def style_agent(state: RepoAnalysisState):
    logger.info("Style Agent: running Ruff/ESLint linting.")

    styler = StyleAgent(
        repo_path=state["repo_path"],
        js_ts_files=state["files"].js_ts_files,
        py_files=state["files"].py_files,
        # log_all_audits=state['log_all_audits'],
    )
    result = styler.run()
    state["style_findings"] = result.get("findings", [])
    return state


def security_agent(state: RepoAnalysisState):
    logger.info("Security Agent: running Bandit/Semgrep.")

    securer = SecurityAgent(
        repo_path=state["repo_path"],
        js_ts_files=state["files"].js_ts_files,
        py_files=state["files"].py_files,
        log_all_audits=state['log_all_audits'],
    )
    result = securer.run()
    state["security_findings"] = result

    return {"security_findings": [{"msg": "Demo security issue"}]}


def performance_agent(state: RepoAnalysisState):
    logger.info("Performance Agent: running Radon.")
    return {"performance_findings": [{"msg": "Demo performance comment"}]}


def conflict_resolver(state: RepoAnalysisState):
    logger.info("Conflict Resolver: merging agent results.")
    merged = (
        str(state.get("style_findings", []))
        + str(state.get("security_findings", []))
        + str(state.get("performance_findings", []))
    )
    return {"merged_findings": merged}


def explainer_agent(state: RepoAnalysisState):
    logger.info("Explainer Agent: summarizing report.")
    # markdown = "\n".join(f"- {f['msg']}" for f in state["merged_findings"])  # type: ignore

    logger.info(f"Cleaning up tmpdir: {state['repo_path']}")
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
