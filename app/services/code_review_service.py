import tempfile
from pathlib import Path
from typing import Any

import requests
import shutil
from app.utils.subprocess_runner import run_safe_subprocess


class CodeReviewService:
    def __init__(self, repo_url: str, ref: str, scan_id: str):
        self.repo_url: str = repo_url
        self.ref: str = ref
        self.scan_id: str = scan_id

    def _repo_exists(self) -> bool:
        """
        Check if the repository exists.
        """

        prefix = "https://github.com/"
        suffix = ".git"
        if not self.repo_url.startswith(prefix) or not self.repo_url.endswith(suffix):
            return False

        response = requests.get(self.repo_url)
        print(response)
        return response.status_code == 200

    def clone_repo(self) -> dict[str, Any]:
        """
        Clone the repository and return the path to the cloned repository.
        """
        try:
            if not self._repo_exists():
                raise Exception("Repository does not exist")

            tmpdir = tempfile.mkdtemp(prefix="marcai-temp-work-")
            if self.ref:
                cmd = ["git", "clone", "--depth", "1", "--branch", self.ref, self.repo_url, tmpdir]
            else:
                cmd = ["git", "clone", "--depth", "1", self.repo_url, tmpdir]

            result = run_safe_subprocess(
                command=cmd,
                cwd=Path("/tmp"),
                timeout=300,
            )

            print("dir: ", tmpdir)
            print("result:", result)

        except Exception as e:
            raise Exception(f"Failed to clone repository: {str(e)}")

        finally:
            # shutil.rmtree(tmpdir)
            pass

        return {"": ""}
    # def get_reviews(self):
    #     return self.review_repository.get_reviews()

    # def add_review(self, review):
    #     self.review_repository.add_review(review)
