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
    stderror: str | None = None
    results: list[BanditFinding] = []


class SemgrepMetadata(BaseModel):
    category: str
    confidence: str
    cwe: list[str]
    impact: str
    license: str
    likelihood: str
    owasp: list[str]
    references: list[str]
    semgrep_dev: dict[str, Any]
    shortlink: str
    source: str
    subcategory: list[str]
    technology: list[str]
    vulnerability_class: list[str]


class SemgrepExtraMetadata(BaseModel):
    engine_kind: str
    fingerprint: str
    fix: str | None
    is_ignored: bool
    lines: str
    message: str
    metadata: SemgrepMetadata
    metavars: dict[str, Any]
    severity: str
    validation_state: str


class SemgrepPosition(BaseModel):
    col: int
    line: int
    offset: int


class SemgrepFinding(BaseModel):
    check_id: str
    end: SemgrepPosition
    extra: SemgrepExtraMetadata
    path: str
    start: SemgrepPosition


class SemgrepFindings(BaseModel):
    errors: list[dict[str, Any]] = []
    results: list[SemgrepFinding] = []
    skipped_rules: list[dict[str, Any]] = []


class SecurityFindings(BaseModel):
    Bandit: BanditFindings
    Semgrep: SemgrepFindings


class SecurityAgent:
    """
    Runs security checks using Bandit and Semgrep.
    """

    def __init__(
        self,
        repo_path: str,
        js_ts_files: int,
        py_files: int,
        log_all_audits: bool = False,
    ) -> None:
        self.repo_path = repo_path
        self.js_ts_files = js_ts_files
        self.py_files = py_files
        self.log_all_audits = log_all_audits

        self.findings = SecurityFindings(
            Bandit=BanditFindings(),
            Semgrep=SemgrepFindings()
        )

    def _run_semgrep(self) -> None:
        """
        Run Semgrep security analysis on all supported files.
        Uses OSS mode with community rules - no login required.
        """
        try:
            # Semgrep command with OSS mode
            cmd = [
                "semgrep",
                "scan",
                "--config",
                "p/security-audit",
                "--config",
                "p/owasp-top-ten",
                "--config",
                "p/secrets",
                "--config",
                "p/supply-chain",
                "--config",
                "p/dockerfile",
                "--json",
                "--quiet",
                self.repo_path,
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=600)

            logger.info(f"Semgrep return code: {result['returncode']}")
            logger.debug(f"Semgrep stdout length: {len(result['stdout'])}")

            self.findings.Semgrep = SemgrepFindings()

            # Semgrep returns 0 (no findings) or 1 (findings found)
            if result["returncode"] in [0, 1] and result["stdout"]:
                output = json.loads(result["stdout"])

                # Parse errors
                self.findings.Semgrep.errors = output.get("errors", [])
                if self.findings.Semgrep.errors:
                    logger.warning(
                        f"Semgrep encountered {len(self.findings.Semgrep.errors)} errors during scan"
                    )

                # Parse skipped rules
                self.findings.Semgrep.skipped_rules = output.get("skipped_rules", [])

                # Parse results
                results = output.get("results", [])
                for item in results:
                    # Parse nested structures
                    start_pos = SemgrepPosition(
                        col=item.get("start", {}).get("col", 0),
                        line=item.get("start", {}).get("line", 0),
                        offset=item.get("start", {}).get("offset", 0),
                    )

                    end_pos = SemgrepPosition(
                        col=item.get("end", {}).get("col", 0),
                        line=item.get("end", {}).get("line", 0),
                        offset=item.get("end", {}).get("offset", 0),
                    )

                    # Parse metadata
                    metadata_dict = item.get("extra", {}).get("metadata", {})
                    metadata = SemgrepMetadata(
                        category=metadata_dict.get("category", ""),
                        confidence=metadata_dict.get("confidence", ""),
                        cwe=metadata_dict.get("cwe", []),
                        impact=metadata_dict.get("impact", ""),
                        license=metadata_dict.get("license", ""),
                        likelihood=metadata_dict.get("likelihood", ""),
                        owasp=metadata_dict.get("owasp", []),
                        references=metadata_dict.get("references", []),
                        semgrep_dev=metadata_dict.get("semgrep.dev", {}),
                        shortlink=metadata_dict.get("shortlink", ""),
                        source=metadata_dict.get("source", ""),
                        subcategory=metadata_dict.get("subcategory", []),
                        technology=metadata_dict.get("technology", []),
                        vulnerability_class=metadata_dict.get(
                            "vulnerability_class", []
                        ),
                    )

                    # Parse extra metadata
                    extra_dict = item.get("extra", {})
                    extra = SemgrepExtraMetadata(
                        engine_kind=extra_dict.get("engine_kind", "OSS"),
                        fingerprint=extra_dict.get("fingerprint", ""),
                        fix=extra_dict.get("fix", None),
                        is_ignored=extra_dict.get("is_ignored", False),
                        lines=extra_dict.get("lines", ""),
                        message=extra_dict.get("message", ""),
                        metadata=metadata,
                        metavars=extra_dict.get("metavars", {}),
                        severity=extra_dict.get("severity", "INFO"),
                        validation_state=extra_dict.get("validation_state", ""),
                    )

                    # Create the finding
                    finding = SemgrepFinding(
                        check_id=item.get("check_id", "unknown"),
                        path=item.get("path", ""),
                        start=start_pos,
                        end=end_pos,
                        extra=extra,
                    )

                    self.findings.Semgrep.results.append(finding)
            else:
                logger.warning(
                    f"Semgrep returned unexpected code: {result['returncode']}"
                )
                if result["stderr"]:
                    logger.warning(f"Semgrep stderr: {result['stderr']}")

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Semgrep JSON output: {e}")
        except Exception as e:
            logger.error(f"Error running Semgrep: {e}")

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
            logger.info(
                f"Bandit Findings: {len(self.findings.Bandit.results)} issues found"
            )
            if self.findings.Bandit.results:
                for finding in self.findings.Bandit.results[:5]:  # Show first 5
                    logger.info(
                        f"  - {finding.issue_severity.value}: {finding.issue_text} ({finding.filename}:{finding.line_number})"
                    )
                if len(self.findings.Bandit.results) > 5:
                    logger.info(
                        f"  ... and {len(self.findings.Bandit.results) - 5} more"
                    )
            else:
                logger.info("Bandit: Not run")

            # Log Semgrep findings
            if self.findings.Semgrep:
                logger.info(
                    f"Semgrep: {len(self.findings.Semgrep.results)} issues found"
                )
                if self.findings.Semgrep.results:
                    for idx, finding in enumerate(self.findings.Semgrep.results[:3]):
                        logger.info(f"  - Finding {idx + 1}:")
                        logger.info(
                            f"    Severity: {finding.extra.severity}"
                        )
                        logger.info(
                            f"    Message: {finding.extra.message} ({finding.path}:{finding.start.line})"
                        )
                    if len(self.findings.Semgrep.results) > 3:
                        logger.info(
                            f"  ... and {len(self.findings.Semgrep.results) - 3} more"
                        )
            else:
                logger.info("Semgrep: Not run")

    def run(self) -> SecurityFindings:
        if self.py_files > 0:
            self._run_bandit()

        # Semgrep supports multiple languages
        if self.py_files > 0 or self.js_ts_files > 0:
            self._run_semgrep()

        self._log_findings()

        return self.findings
