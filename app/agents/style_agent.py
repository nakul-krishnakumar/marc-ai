from typing import Any
import os
import json
import shutil
from app.utils.subprocess_runner import run_safe_subprocess
from app.core.logger import logger


class StyleAgent:
    """
    Runs style and formatting checks using Ruff (Python) and ESLint (JS).
    """

    def __init__(self, repo_path: str, js_ts_files: int, py_files: int, log_all_audits: bool = False) -> None:
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
            minimal_package = {
                "name": "temp-eslint-analysis",
                "version": "1.0.0",
                "private": True
            }
            with open(package_json, "w") as f:
                json.dump(minimal_package, f)
            temp_package_created = True

        # Install ESLint dependencies locally in the temp directory
        logger.info("Installing ESLint dependencies in temp directory...")
        install_cmd = [
            "npm", "install", "--no-save", "--silent",
            "eslint",
            "@typescript-eslint/parser",
            "@typescript-eslint/eslint-plugin"
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
                self.findings.append({
                    "tool": "eslint",
                    "output": json.loads(eslint_result["stdout"]),
                    "errors": eslint_result["stderr"]
                })

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

        if ruff_result["stdout"]:
            self.findings.append(
                {
                    "tool": "ruff",
                    "output": ruff_result["stdout"],
                    "errors": ruff_result["stderr"],
                }
            )

    def run(self) -> dict[str, Any]:
        """Run style checks on the repository."""

        if self.py_files > 0:
            self._run_ruff_linting()
        if self.js_ts_files > 0:
            self._run_eslint_linting()

        if self.log_all_audits:
            logger.info("Style agent findings:")
            for i in self.findings:
                logger.info(f"Tool: {i.get('tool')}")

                results = i.get("output", [])["results"]
                for result in results:
                    logger.info(f"File: {result.get('filePath')}")
                    for message in result.get("messages", []):
                        logger.info(
                            f"  Line {message.get('line')}, Col {message.get('column')}: {message.get('message')} ({message.get('ruleId')})\n"
                        )

                logger.debug(f"Errors: {i.get('errors')}")
                logger.info("-----\n")

        return {
            "agent": "style",
            "findings": self.findings
        }
