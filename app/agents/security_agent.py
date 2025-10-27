import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, HttpUrl

from app.core.logger import logger
from app.utils.subprocess_runner import run_safe_subprocess


class IssueType(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNDEFINED = "UNDEFINED"


class IssueCWE(BaseModel):
    id: int
    link: HttpUrl


class BanditFinding(BaseModel):
    code: str
    col_offset: int
    end_col_offset: int
    filename: Path
    issue_confidence: IssueType
    issue_cwe: IssueCWE
    issue_severity: IssueType
    issue_text: str
    line_number: int
    line_range: list[int]
    more_info: HttpUrl
    test_id: str
    test_name: str


class BanditFindings(BaseModel):
    bandit_errors: dict[str, str] | None = None
    stderror: str
    results: list[BanditFinding]


class SecurityFindings(BaseModel):
    Bandit: BanditFindings | None = None
    Semgrep: dict[str, Any] | None = None


class SecurityAgent:
    """
    Runs security checks using Bandit and Semgrep.
    """

    def __init__(
        self, repo_path: str, js_ts_files: int, py_files: int, log_all_audits: bool = False
    ) -> None:
        self.repo_path = repo_path
        self.js_ts_files = js_ts_files
        self.py_files = py_files
        self.log_all_audits = log_all_audits

        self.findings = SecurityFindings()
    
    def _run_semgrep(self) -> None:
        """
        Run Semgrep security analysis on the repository.
        """

        cmd = ["semgrep", "--config", "auto", "--json"]
        result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

        logger.info(f"Semgrep return code: {result['returncode']}")
        logger.debug(f"Semgrep stdout length: {len(result['stdout'])}")
        logger.debug(f"Semgrep stderr: {result['stderr'][:200]}")

        self.findings.Semgrep = {
            "stderror": result["stderr"],
            "results": [],
        }

        # Semgrep returns exit code 1 when it finds issues (normal behavior)
        if result["returncode"] in [0, 1] and result["stdout"]:
            output = json.loads(result["stdout"])
            results = output.get("results", [])
            logger.info(f"Semgrep found {len(results)} security issues")
            self.findings.Semgrep["results"] = results

    def _run_bandit(self) -> None:
        """
        Run Bandit security analysis on Python files.
        """

        cmd = ["bandit", "-r", self.repo_path, "-f", "json"]
        result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

        logger.info(f"Bandit return code: {result['returncode']}")
        logger.debug(f"Bandit stdout length: {len(result['stdout'])}")
        logger.debug(f"Bandit stderr: {result['stderr'][:200]}")

        self.findings.Bandit = BanditFindings(
            stderror=result["stderr"],
            results=[],
        )

        # Bandit returns exit code 1 when it finds issues (normal behavior)
        if result["returncode"] in [0, 1] and result["stdout"]:
            output = json.loads(result["stdout"])
            self.findings.Bandit.bandit_errors = output.get("errors", None)

            results = output.get("results", [])
            logger.info(f"Bandit found {len(results)} security issues")
            for item in results:
                # Parse CWE - it's a dict with 'id' and 'link' keys
                cwe_data = item.get("issue_cwe", {})
                if isinstance(cwe_data, dict):
                    cwe_id = cwe_data.get("id", 0)
                    cwe_link = cwe_data.get("link", "https://cwe.mitre.org/")
                else:
                    # Fallback for unexpected format
                    cwe_id = 0
                    cwe_link = "https://cwe.mitre.org/"

                issue_cwe = IssueCWE(id=cwe_id, link=HttpUrl(cwe_link))

                finding = BanditFinding(
                    code=item["code"],
                    col_offset=item["col_offset"],
                    end_col_offset=item["end_col_offset"],
                    filename=Path(item["filename"]),
                    issue_confidence=IssueType(item["issue_confidence"].upper()),
                    issue_cwe=issue_cwe,
                    issue_severity=IssueType(item["issue_severity"].upper()),
                    issue_text=item["issue_text"],
                    line_number=item["line_number"],
                    line_range=item["line_range"],
                    more_info=item["more_info"],
                    test_id=item["test_id"],
                    test_name=item["test_name"],
                )

                self.findings.Bandit.results.append(finding)

    def _log_findings(self):
        logger.info("Security Agent findings:")
        if self.findings.Bandit:
            logger.info(f"Bandit Findings: {len(self.findings.Bandit.results)} issues found")
            if self.findings.Bandit.results:
                for finding in self.findings.Bandit.results[:5]:  # Show first 5
                    logger.info(
                        f"  - {finding.issue_severity.value}: {finding.issue_text} ({finding.filename}:{finding.line_number})"
                    )
                if len(self.findings.Bandit.results) > 5:
                    logger.info(f"  ... and {len(self.findings.Bandit.results) - 5} more")
        else:
            logger.info("Bandit Findings: Not run")

        if self.log_all_audits:
            logger.info("Full Security Findings:")
            logger.info(self.findings.model_dump_json(indent=3))

    def run(self) -> SecurityFindings:
        if self.py_files > 0:
            self._run_bandit()
        # if self.py_files > 0 or self.js_ts_files > 0:
        # self._run_semgrep()

        self._log_findings()

        return self.findings
