import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.core.logger import logger
from app.utils.subprocess_runner import run_safe_subprocess


class CyclomaticComplexity(BaseModel):
    """Cyclomatic Complexity metrics from Radon CC"""
    type: str  # function, method, class
    rank: str  # A, B, C, D, E, F
    complexity: int
    col_offset: int
    name: str
    endline: int
    lineno: int
    classname: str | None = None
    closures: list[Any] = []


class MaintainabilityIndex(BaseModel):
    """Maintainability Index from Radon MI"""
    rank: str  # A, B, C
    mi: float  # Maintainability Index score (0-100)


class RawMetrics(BaseModel):
    """Raw code metrics from Radon"""
    loc: int  # Lines of Code
    lloc: int  # Logical Lines of Code
    sloc: int  # Source Lines of Code
    comments: int
    multi: int  # Multi-line strings
    blank: int
    single_comments: int


class HalsteadMetrics(BaseModel):
    """Halstead complexity metrics"""
    h1: int  # Number of distinct operators
    h2: int  # Number of distinct operands
    N1: int  # Total number of operators
    N2: int  # Total number of operands
    vocabulary: int
    length: int
    calculated_length: float
    volume: float
    difficulty: float
    effort: float
    time: float
    bugs: float


class HalsteadFileMetrics(BaseModel):
    """Halstead metrics for an entire file"""
    total: HalsteadMetrics
    functions: dict[str, HalsteadMetrics] = {}


class RadonFindings(BaseModel):
    """Combined Radon metrics for all files"""
    cc: dict[str, list[CyclomaticComplexity]] = {}  # filepath -> list of CC metrics
    mi: dict[str, MaintainabilityIndex] = {}  # filepath -> MI score
    raw: dict[str, RawMetrics] = {}  # filepath -> raw metrics
    hal: dict[str, HalsteadFileMetrics] = {}  # filepath -> Halstead metrics


class XenonViolation(BaseModel):
    """Xenon threshold violations"""
    path: Path
    function: str
    line: int
    complexity: int
    rank: str


class PerformanceFindings(BaseModel):
    """All performance analysis findings"""
    radon: RadonFindings = RadonFindings()
    xenon_violations: list[XenonViolation] = []
    summary: dict[str, Any] = {}


class PerformanceAgent:
    """
    Runs performance and complexity analysis using Radon and Xenon.
    Only analyzes Python files.
    """

    def __init__(
        self,
        repo_path: str,
        py_files: int,
        log_all_audits: bool = False
    ) -> None:
        self.repo_path = repo_path
        self.py_files = py_files
        self.log_all_audits = log_all_audits
        self.findings = PerformanceFindings()

    def _run_radon_cc(self) -> dict[str, list[dict]]:
        """Run Radon Cyclomatic Complexity analysis."""
        try:
            cmd = [
                "radon", "cc",
                self.repo_path,
                "--json",
                "--min", "C",  # Only report C and above
                # "--exclude", "*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

            if result["returncode"] == 0 and result["stdout"]:
                data = json.loads(result["stdout"])
                logger.info(f"Radon CC analyzed {len(data)} files")
                return data
            else:
                logger.warning(f"Radon CC returned code {result['returncode']}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Radon CC JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error running Radon CC: {e}")
            return {}

    def _run_radon_mi(self) -> dict[str, dict]:
        """Run Radon Maintainability Index analysis."""
        try:
            cmd = [
                "radon", "mi",
                self.repo_path,
                "--json",
                # "--exclude", "*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

            if result["returncode"] == 0 and result["stdout"]:
                data = json.loads(result["stdout"])
                logger.info(f"Radon MI analyzed {len(data)} files")
                return data
            else:
                logger.warning(f"Radon MI returned code {result['returncode']}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Radon MI JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error running Radon MI: {e}")
            return {}

    def _run_radon_raw(self) -> dict[str, dict]:
        """Run Radon Raw Metrics analysis."""
        try:
            cmd = [
                "radon", "raw",
                self.repo_path,
                "--json",
                # "--exclude", "*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

            if result["returncode"] == 0 and result["stdout"]:
                data = json.loads(result["stdout"])
                logger.info(f"Radon Raw analyzed {len(data)} files")
                return data
            else:
                logger.warning(f"Radon Raw returned code {result['returncode']}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Radon Raw JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error running Radon Raw: {e}")
            return {}

    def _run_radon_hal(self) -> dict[str, dict]:
        """Run Radon Halstead Metrics analysis."""
        try:
            cmd = [
                "radon", "hal",
                self.repo_path,
                "--json",
                # "--exclude", "*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

            if result["returncode"] == 0 and result["stdout"]:
                data = json.loads(result["stdout"])
                logger.info(f"Radon Halstead analyzed {len(data)} files")
                return data
            else:
                logger.warning(f"Radon Halstead returned code {result['returncode']}")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Radon Halstead JSON: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error running Radon Halstead: {e}")
            return {}

    def _run_xenon(self) -> None:
        """Run Xenon to enforce complexity thresholds."""
        try:
            cmd = [
                "xenon",
                self.repo_path,
                "--max-absolute", "B",
                "--max-modules", "B",
                "--max-average", "A",
                # "--exclude", "*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"
            ]

            result = run_safe_subprocess(cmd, cwd=self.repo_path, timeout=300)

            if result["returncode"] != 0:
                logger.info("Xenon found complexity violations")
                if result["stdout"]:
                    self._parse_xenon_output(result["stdout"])
            else:
                logger.info("Xenon: All complexity thresholds passed")

        except Exception as e:
            logger.error(f"Error running Xenon: {e}")

    def _parse_xenon_output(self, output: str) -> None:
        """Parse Xenon text output to extract violations."""
        lines = output.strip().split('\n')
        for line in lines:
            if ':' in line and 'too complex' in line.lower():
                try:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        path = parts[0].strip()
                        line_no = int(parts[1].strip())

                        msg = ':'.join(parts[3:])
                        if "'" in msg:
                            func_name = msg.split("'")[1]
                            complexity = int(msg.split('(')[-1].split(')')[0])

                            violation = XenonViolation(
                                path=Path(path),
                                function=func_name,
                                line=line_no,
                                complexity=complexity,
                                rank=self._complexity_to_rank(complexity)
                            )
                            self.findings.xenon_violations.append(violation)
                except Exception as e:
                    logger.debug(f"Could not parse Xenon line: {line} - {e}")

    def _complexity_to_rank(self, complexity: int) -> str:
        """Convert complexity score to rank (A-F)"""
        if complexity <= 5:
            return "A"
        elif complexity <= 10:
            return "B"
        elif complexity <= 20:
            return "C"
        elif complexity <= 30:
            return "D"
        elif complexity <= 40:
            return "E"
        else:
            return "F"

    def _consolidate_metrics(
        self,
        cc_data: dict,
        mi_data: dict,
        raw_data: dict,
        hal_data: dict
    ) -> None:
        """Consolidate all Radon metrics into findings."""
        # Process CC data
        for filepath, cc_list in cc_data.items():
            try:
                self.findings.radon.cc[filepath] = [
                    CyclomaticComplexity(**item) for item in cc_list
                ]
            except Exception as e:
                logger.debug(f"Error parsing CC for {filepath}: {e}")

        # Process MI data
        for filepath, mi_item in mi_data.items():
            try:
                self.findings.radon.mi[filepath] = MaintainabilityIndex(**mi_item)
            except Exception as e:
                logger.debug(f"Error parsing MI for {filepath}: {e}")

        # Process Raw data
        for filepath, raw_item in raw_data.items():
            try:
                self.findings.radon.raw[filepath] = RawMetrics(**raw_item)
            except Exception as e:
                logger.debug(f"Error parsing Raw for {filepath}: {e}")

        # Process Halstead data
        for filepath, hal_item in hal_data.items():
            try:
                if isinstance(hal_item, dict):
                    total_metrics = HalsteadMetrics(**hal_item.get("total", {}))

                    functions_data = hal_item.get("functions", {})
                    function_metrics = {}
                    for func_name, func_data in functions_data.items():
                        if isinstance(func_data, dict):
                            function_metrics[func_name] = HalsteadMetrics(**func_data)

                    self.findings.radon.hal[filepath] = HalsteadFileMetrics(
                        total=total_metrics,
                        functions=function_metrics
                    )
            except Exception as e:
                logger.debug(f"Error parsing Halstead for {filepath}: {e}")

    def _generate_summary(self) -> None:
        """Generate summary statistics"""
        total_files = len(set(
            list(self.findings.radon.cc.keys()) +
            list(self.findings.radon.mi.keys()) +
            list(self.findings.radon.raw.keys())
        ))

        total_functions = sum(len(cc_list) for cc_list in self.findings.radon.cc.values())

        # Count complexity ranks
        complexity_ranks = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "F": 0}
        for cc_list in self.findings.radon.cc.values():
            for cc in cc_list:
                complexity_ranks[cc.rank] = complexity_ranks.get(cc.rank, 0) + 1

        # Average MI
        mi_scores = [mi.mi for mi in self.findings.radon.mi.values()]
        avg_mi = sum(mi_scores) / len(mi_scores) if mi_scores else 0

        # Total LOC
        total_loc = sum(raw.loc for raw in self.findings.radon.raw.values())

        self.findings.summary = {
            "total_files_analyzed": total_files,
            "total_functions": total_functions,
            "complexity_distribution": complexity_ranks,
            "average_maintainability_index": round(avg_mi, 2),
            "total_lines_of_code": total_loc,
            "xenon_violations": len(self.findings.xenon_violations)
        }

    def run(self) -> PerformanceFindings:
        """Run all performance analysis tools"""
        if self.py_files == 0:
            logger.info("Performance Agent: No Python files to analyze")
            return self.findings

        logger.info("Performance Agent: Running Radon and Xenon analysis")

        # Run all Radon metrics
        cc_data = self._run_radon_cc()
        mi_data = self._run_radon_mi()
        raw_data = self._run_radon_raw()
        hal_data = self._run_radon_hal()

        # Consolidate metrics
        self._consolidate_metrics(cc_data, mi_data, raw_data, hal_data)

        # Run Xenon threshold checks
        self._run_xenon()

        # Generate summary
        self._generate_summary()

        if self.log_all_audits:
            logger.info("Performance Agent findings:")
            logger.info(f"  Files analyzed: {self.findings.summary.get('total_files_analyzed', 0)}")
            logger.info(f"  Functions analyzed: {self.findings.summary.get('total_functions', 0)}")
            logger.info(f"  Average MI: {self.findings.summary.get('average_maintainability_index', 0)}")
            logger.info(f"  Total LOC: {self.findings.summary.get('total_lines_of_code', 0)}")
            logger.info(f"  Xenon violations: {len(self.findings.xenon_violations)}")

            if self.findings.xenon_violations:
                logger.info("  Top violations:")
                for violation in self.findings.xenon_violations[:3]:
                    logger.info(f"    - {violation.function} ({violation.path}:{violation.line}) - Complexity: {violation.complexity}")

        return self.findings
