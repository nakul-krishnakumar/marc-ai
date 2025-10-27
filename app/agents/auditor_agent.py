import fnmatch
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel


class Files(BaseModel):
    readmes: list[Path]
    package_jsons: list[Path]
    requirements_txts: list[Path]
    pyproject_tomls: list[Path]
    dir_tree: list[dict[str, Any]]
    js_ts_files: int = 0
    py_files: int = 0


class AuditorAgent:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.files = Files(
            readmes=[], package_jsons=[], requirements_txts=[], pyproject_tomls=[], dir_tree=[]
        )

        self.ignore_dirs = [
            # Version control
            ".git",
            ".svn",
            ".hg",
            ".bzr",
            # Python
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "venv",
            ".venv",
            "env",
            ".env",
            "virtualenv",
            "*.egg-info",
            ".eggs",
            "dist",
            "build",
            ".tox",
            "htmlcov",
            ".coverage",
            "coverage",
            # Node.js
            "node_modules",
            ".npm",
            ".yarn",
            ".pnp",
            # IDEs
            ".idea",
            ".vscode",
            ".vs",
            ".eclipse",
            ".settings",
            # Build outputs
            "dist",
            "build",
            "out",
            "target",
            ".next",
            ".nuxt",
            # Caches
            ".cache",
            ".parcel-cache",
            ".turbo",
            # OS
            ".Trash",
            "Thumbs.db",
            # Logs
            "logs",
            "*.log",
        ]

        self.ignore_files = [
            # OS files
            ".DS_Store",
            "Thumbs.db",
            "desktop.ini",
            # Editor files
            ".swp",
            ".swo",
            "*~",
            "*.bak",
            "*.tmp",
            # Lock files
            # "package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock",
            # Environment files (sensitive)
            ".env",
            ".env.local",
            ".env.production",
            # Compiled files
            "*.pyc",
            "*.pyo",
            "*.so",
            "*.dll",
            "*.dylib",
            "*.exe",
            # Archives
            "*.zip",
            "*.tar",
            "*.gz",
            "*.rar",
            "*.7z",
            # Media files
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.ico",
            "*.svg",
            "*.mp4",
            "*.mp3",
            "*.wav",
            "*.avi",
            # Fonts
            "*.woff",
            "*.woff2",
            "*.ttf",
            "*.eot",
            "*.otf",
            # Database files
            "*.db",
            "*.sqlite",
            "*.sqlite3",
        ]

        self.ignore_patterns = [
            "*.pyc",
            "*.pyo",
            "*.so",
            "*.dll",
            "*.log",
            "*.tmp",
            "*.bak",
            "*.egg-info",
            "__pycache__",
        ]

        self.js_ts_patterns = [".js", ".jsx", ".ts", ".tsx"]
        self.py_patterns = [".py"]

    def _should_ignore_file(self, filename: str) -> bool:
        """Check if file should be ignored based on patterns."""
        # Check exact matches
        if filename in self.ignore_files:
            return True

        # Check pattern matches (*.pyc, *.log, etc.)
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(filename, pattern):
                return True

        # Check file extensions
        file_ext = Path(filename).suffix.lower()
        ignore_extensions = {
            ".pyc",
            ".pyo",
            ".so",
            ".dll",
            ".exe",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".ico",
            ".svg",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".otf",
            ".mp4",
            ".mp3",
            ".wav",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".db",
            ".sqlite",
            ".sqlite3",
            ".log",
            ".tmp",
            ".bak",
        }

        if file_ext in ignore_extensions:
            return True

        return False

    def _should_ignore_dir(self, dirname: str) -> bool:
        """Check if directory should be ignored."""
        # Check exact matches
        if dirname in self.ignore_dirs:
            return True

        # Check if starts with dot (hidden directories)
        if dirname.startswith("."):
            return True

        # Check pattern matches
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(dirname, pattern):
                return True

        return False

    def _handle_files(self, root: str, files: list[str]) -> None:
        """Process individual file based on its type."""
        for file in files:
            # Skip ignored files
            if self._should_ignore_file(file):
                continue

            file_path = Path(root) / file

            # Skip if file doesn't exist or can't be accessed
            try:
                file_size = os.path.getsize(file_path)
            except (OSError, PermissionError):
                continue

            # Categorize important files
            if file.lower() == "readme.md":
                self.files.readmes.append(file_path)
            elif file == "package.json":
                self.files.package_jsons.append(file_path)
            elif file == "requirements.txt":
                self.files.requirements_txts.append(file_path)
            elif file == "pyproject.toml":
                self.files.pyproject_tomls.append(file_path)

            print(file_path.suffix)

            if file_path.suffix in self.js_ts_patterns:
                self.files.js_ts_files += 1
            elif file_path.suffix in self.py_patterns:
                self.files.py_files += 1

            self.files.dir_tree.append(
                {"name": file, "path": str(file_path), "size": file_size, "type": "file"}
            )

        return

    def _handle_directories(self, root: str, dirs: list[str]) -> None:
        """Process individual directories to update directory tree."""
        # Filter out ignored directories IN-PLACE
        # This modifies the dirs list that os.walk uses, preventing recursion into ignored dirs
        dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]

        for dir_name in dirs:
            dir_path = Path(root) / dir_name

            # Skip if directory doesn't exist or can't be accessed
            if not dir_path.exists() or not dir_path.is_dir():
                continue

            self.files.dir_tree.append(
                {"name": dir_name, "path": str(dir_path), "type": "directory"}
            )

        return

    def generate_dir_metadata(self, log_all: bool = False) -> Files:
        """
        Generate metadata for the directory by walking
        through the directory and creating directory tree.
        """

        for root, dirs, files in os.walk(self.repo_path):
            self._handle_files(root, files)
            self._handle_directories(root, dirs)

        print("Generated directory metadata:")
        print(f"Found {len(self.files.readmes)} readme files.")
        print(f"Found {len(self.files.package_jsons)} package.json files.")
        print(f"Found {len(self.files.requirements_txts)} requirements.txt files.")
        print(f"Found {len(self.files.pyproject_tomls)} pyproject.toml files.")
        print(f"Found {self.files.js_ts_files} JavaScript/TypeScript files.")
        print(f"Found {self.files.py_files} Python files.")
        print(f"Total files and directories processed: {len(self.files.dir_tree)}")

        if log_all:
            for file in self.files.readmes:
                print(
                    "Readme file found:",
                    file,
                )
            print("\n")

            for file in self.files.package_jsons:
                print(
                    "package.json file found:",
                    file,
                )
            print("\n")

            for file in self.files.requirements_txts:
                print(
                    "requirements.txt file found:",
                    file,
                )
            print("\n")

            for file in self.files.pyproject_tomls:
                print(
                    "pyproject.toml file found:",
                    file,
                )
            print("\n")

            for file in self.files.dir_tree:
                for key, value in file.items():
                    print(f"{key}: {value}\n")
                print("-----\n")
            print("\n")

        return self.files
