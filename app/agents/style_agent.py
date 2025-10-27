import json
import os
import shutil
from typing import Any

from app.core.logger import logger
from app.utils.subprocess_runner import run_safe_subprocess


class StyleAgent:
    """
    Runs style and formatting checks using Ruff (Python) and ESLint (JS).
    """

    def __init__(
        self, repo_path: str, js_ts_files: int, py_files: int, log_all_audits: bool = False
    ) -> None:
        self.repo_path = repo_path
        self.findings = []
        self.js_ts_files = js_ts_files
        self.py_files = py_files
        self.log_all_audits = log_all_audits

    def _run_eslint_linting(self):
        """
        Run eslint with fallback config generation
        """
        config_file = os.path.join(self.repo_path, "eslint.config.js")
        package_json = os.path.join(self.repo_path, "package.json")
        temp_config_created = False
        temp_package_created = False

        # Create package.json if it doesn't exist
        if not os.path.exists(package_json):
            minimal_package = {"name": "temp-eslint-analysis", "version": "1.0.0", "private": True}
            with open(package_json, "w") as f:
                json.dump(minimal_package, f)
            temp_package_created = True

        # Install ESLint dependencies locally in the temp directory
        logger.info("Installing ESLint dependencies in temp directory...")
        install_cmd = [
            "npm",
            "install",
            "--no-save",
            "--silent",
            "eslint",
            "@typescript-eslint/parser",
            "@typescript-eslint/eslint-plugin",
        ]
        install_result = run_safe_subprocess(install_cmd, cwd=self.repo_path, timeout=120)

        if install_result["returncode"] != 0:
            logger.error(f"Failed to install ESLint dependencies: {install_result['stderr']}")
            # Cleanup and return
            if temp_package_created and os.path.exists(package_json):
                os.remove(package_json)
            return

        # Check if config exists, then create minimal one with TypeScript support
        if not os.path.exists(config_file):
            minimal_config = """
const tsParser = require("@typescript-eslint/parser");
const tsPlugin = require("@typescript-eslint/eslint-plugin");

module.exports = [
    {
        files: ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"],
        languageOptions: {
            ecmaVersion: "latest",
            sourceType: "module",
            parser: tsParser,
            parserOptions: {
                ecmaFeatures: {
                    jsx: true
                }
            }
        },
        plugins: {
            "@typescript-eslint": tsPlugin
        },
        rules: {
            "no-unused-vars": "warn",
            "no-undef": "warn",
            "semi": "warn",
            "@typescript-eslint/no-unused-vars": "warn",
            "@typescript-eslint/no-explicit-any": "warn"
        }
    }
];
            """
            with open(config_file, "w") as f:
                f.write(minimal_config)
            temp_config_created = True

        try:
            cmd = ["npx", "eslint", "--format", "json-with-metadata", self.repo_path]
            eslint_result = run_safe_subprocess(cmd, cwd=self.repo_path)

            if eslint_result["stdout"]:
                self.findings.append(
                    {
                        "tool": "eslint",
                        "output": json.loads(eslint_result["stdout"]),
                        "errors": eslint_result["stderr"],
                    }
                )

        finally:
            # Cleanup temporary files
            if temp_config_created and os.path.exists(config_file):
                os.remove(config_file)
            if temp_package_created and os.path.exists(package_json):
                os.remove(package_json)
            # Cleanup node_modules
            node_modules = os.path.join(self.repo_path, "node_modules")
            if os.path.exists(node_modules):
                shutil.rmtree(node_modules, ignore_errors=True)

    def _run_ruff_linting(self):
        """
        Run ruff linting for Python files
        """
        cmd = ["ruff", "check", self.repo_path, "--output-format=json"]
        ruff_result = run_safe_subprocess(cmd, cwd=self.repo_path)

        logger.info(f"Ruff return code: {ruff_result['returncode']}")

        # Ruff returns exit code 1 when it finds issues (normal behavior)
        if ruff_result["returncode"] in [0, 1] and ruff_result["stdout"]:
            try:
                # Parse JSON output
                output = json.loads(ruff_result["stdout"])
                logger.info(f"Ruff found {len(output)} issues")

                self.findings.append(
                    {
                        "tool": "ruff",
                        "output": output,  # Store parsed JSON, not string
                        "errors": ruff_result["stderr"],
                    }
                )
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Ruff JSON output: {e}")
                logger.debug(f"Raw stdout: {ruff_result['stdout'][:500]}")
        else:
            logger.info(f"Ruff found no issues or failed. Return code: {ruff_result['returncode']}")

    def run(self) -> dict[str, Any]:
        """Run style checks on the repository."""

        if self.py_files > 0:
            self._run_ruff_linting()
        if self.js_ts_files > 0:
            self._run_eslint_linting()

        if self.log_all_audits:
            logger.info("Style Agent findings summary:")
            for finding in self.findings:
                tool = finding.get('tool')
                output = finding.get('output')

                if tool == 'ruff' and isinstance(output, list):
                    # Show first 3 issues
                    for issue in output[:3]:
                        logger.info(f"    - {issue.get('code')}: {issue.get('message')} ({issue.get('filename')}:{issue.get('location', {}).get('row')})")
                    if len(output) > 3:
                        logger.info(f"    ... and {len(output) - 3} more")

                elif tool == 'eslint' and isinstance(output, dict):
                    results = output.get('results', [])
                    total_warnings = sum(r.get('warningCount', 0) for r in results)
                    total_errors = sum(r.get('errorCount', 0) for r in results)
                    logger.info(f"  ESLint: {len(results)} files analyzed, {total_warnings} warnings, {total_errors} errors")

        return {"agent": "style", "findings": self.findings}
