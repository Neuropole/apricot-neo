"""Git inspection tools for Phase 1.3.

These tools run `git` subprocesses safely (no shell), capture stdout/stderr,
and gracefully handle non-git directories and command failures.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apricot.tools.base import BaseTool, ToolResult


@dataclass(frozen=True)
class _GitRunResult:
    exit_code: int
    stdout: str
    stderr: str


class GitToolBase(BaseTool):
    """Shared git runner implementation."""

    def __init__(self, repo_root: str | Path) -> None:
        self._repo_root = Path(repo_root).resolve(strict=False)

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    def _run_git(
        self,
        args: list[str],
        *,
        timeout_s: int = 20,
        max_output_bytes: int = 250_000,
    ) -> _GitRunResult:
        # subprocess.run with list arguments => no shell injection surface.
        try:
            proc = subprocess.run(
                ["git", *args],
                cwd=str(self._repo_root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_s,
                check=False,
            )
        except FileNotFoundError:
            return _GitRunResult(exit_code=127, stdout="", stderr="git executable not found")
        except NotADirectoryError:
            return _GitRunResult(
                exit_code=126, stdout="", stderr="repository root is not a directory"
            )
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout if isinstance(exc.stdout, str) else ""
            stderr = exc.stderr if isinstance(exc.stderr, str) else ""
            return _GitRunResult(exit_code=124, stdout=stdout, stderr=f"git timed out: {stderr}")

        stdout = proc.stdout or ""
        stderr = proc.stderr or ""

        # Truncate to keep ToolResult payload size manageable.
        if len(stdout.encode("utf-8", errors="replace")) > max_output_bytes:
            stdout = (
                stdout.encode("utf-8", errors="replace")[:max_output_bytes].decode(
                    "utf-8", errors="replace"
                )
                + "\n…(truncated)…"
            )
        if len(stderr.encode("utf-8", errors="replace")) > max_output_bytes:
            stderr = (
                stderr.encode("utf-8", errors="replace")[:max_output_bytes].decode(
                    "utf-8", errors="replace"
                )
                + "\n…(truncated)…"
            )

        return _GitRunResult(exit_code=proc.returncode, stdout=stdout, stderr=stderr)

    def _not_a_git_repo_failure(self, run_res: _GitRunResult) -> bool:
        # Heuristic: git emits these messages in non-repo contexts.
        combined = (run_res.stdout + "\n" + run_res.stderr).lower()
        return (
            "not a git repository" in combined
            or "fatal: not a git repository" in combined
            or "unknown revision" in combined
        )


class GitStatusTool(GitToolBase):
    """Run `git status` in the repository."""

    @property
    def name(self) -> str:
        return "git_status"

    @property
    def description(self) -> str:
        return "Get concise `git status` output for the repository (porcelain + branch)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {"type": "object", "properties": {}}

    def execute(self, **_: Any) -> ToolResult:
        run_res = self._run_git(["status", "--porcelain=v1", "-b"])
        if run_res.exit_code != 0:
            return ToolResult.failure(
                error="git_status failed",
                output=json.dumps(
                    {
                        "type": "git_status",
                        "exit_code": run_res.exit_code,
                        "stdout": run_res.stdout,
                        "stderr": run_res.stderr,
                    },
                    ensure_ascii=False,
                ),
                metadata={"exit_code": run_res.exit_code, "stderr": run_res.stderr},
            )

        payload = {
            "type": "git_status",
            "exit_code": run_res.exit_code,
            "stdout": run_res.stdout,
            "stderr": run_res.stderr,
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"exit_code": run_res.exit_code},
        )


class GitDiffTool(GitToolBase):
    """Run `git diff` in the repository."""

    @property
    def name(self) -> str:
        return "git_diff"

    @property
    def description(self) -> str:
        return "Get `git diff` output (working tree or staged) for the repository."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "staged": {"type": "boolean", "description": "Show staged diff."},
                "path": {"type": "string", "description": "Optional pathspec."},
                "max_bytes": {"type": "integer", "description": "Max output bytes."},
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        staged_raw = kwargs.get("staged", False)
        staged = staged_raw if isinstance(staged_raw, bool) else bool(staged_raw)

        path_raw = kwargs.get("path")
        path = path_raw if isinstance(path_raw, str) else None

        try:
            max_bytes = int(kwargs.get("max_bytes", 250_000))
        except (TypeError, ValueError):
            return ToolResult.failure(error="max_bytes must be an integer")

        args = ["diff"]
        if staged:
            args = ["diff", "--cached"]
        if path:
            args.extend(["--", path])

        run_res = self._run_git(args, max_output_bytes=max_bytes)
        if run_res.exit_code != 0:
            return ToolResult.failure(
                error="git_diff failed",
                output=json.dumps(
                    {
                        "type": "git_diff",
                        "exit_code": run_res.exit_code,
                        "stdout": run_res.stdout,
                        "stderr": run_res.stderr,
                    },
                    ensure_ascii=False,
                ),
                metadata={"exit_code": run_res.exit_code, "stderr": run_res.stderr},
            )

        payload = {
            "type": "git_diff",
            "exit_code": run_res.exit_code,
            "stdout": run_res.stdout,
            "stderr": run_res.stderr,
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"exit_code": run_res.exit_code},
        )


class GitLogTool(GitToolBase):
    """Run `git log` and return parsed structured entries."""

    @property
    def name(self) -> str:
        return "git_log"

    @property
    def description(self) -> str:
        return "Get recent commit history (parsed into structured entries)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "max_count": {"type": "integer", "description": "Max commits to return."},
                "path": {"type": "string", "description": "Optional pathspec."},
                "max_bytes": {"type": "integer", "description": "Max output bytes."},
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        try:
            max_count = int(kwargs.get("max_count", 20))
            max_bytes = int(kwargs.get("max_bytes", 250_000))
        except (TypeError, ValueError):
            return ToolResult.failure(error="max_count/max_bytes must be integers")

        path_raw = kwargs.get("path")
        path = path_raw if isinstance(path_raw, str) else None

        sep1 = "\x1f"
        sep2 = "\x1e"
        pretty = f"%H{sep1}%ad{sep1}%s{sep2}"
        args = [
            "log",
            f"-n{max_count}",
            f"--pretty=format:{pretty}",
            "--date=iso-strict",
            "--no-color",
        ]
        if path:
            args.extend(["--", path])

        run_res = self._run_git(args, max_output_bytes=max_bytes)
        if run_res.exit_code != 0:
            return ToolResult.failure(
                error="git_log failed",
                output=json.dumps(
                    {
                        "type": "git_log",
                        "exit_code": run_res.exit_code,
                        "stdout": run_res.stdout,
                        "stderr": run_res.stderr,
                    },
                    ensure_ascii=False,
                ),
                metadata={"exit_code": run_res.exit_code, "stderr": run_res.stderr},
            )

        entries: list[dict[str, Any]] = []
        for rec in run_res.stdout.split(sep2):
            if not rec:
                continue
            parts = rec.split(sep1)
            if len(parts) != 3:
                continue
            commit_hash, date_str, subject = parts
            entries.append({"hash": commit_hash, "date": date_str, "subject": subject})

        payload = {
            "type": "git_log",
            "exit_code": run_res.exit_code,
            "commits": entries,
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"count": len(entries)},
        )


class GitShowTool(GitToolBase):
    """Run `git show` for a given revision."""

    @property
    def name(self) -> str:
        return "git_show"

    @property
    def description(self) -> str:
        return "Show commit/file revision contents via `git show`."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "rev": {
                    "type": "string",
                    "description": "Revision hash/ref to show (e.g. HEAD~1).",
                },
                "max_bytes": {"type": "integer", "description": "Max output bytes."},
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        rev_raw = kwargs.get("rev")
        if not isinstance(rev_raw, str) or not rev_raw.strip():
            return ToolResult.failure(error="rev must be a non-empty string")
        rev = rev_raw.strip()

        max_bytes_raw = kwargs.get("max_bytes", 250_000)
        try:
            max_bytes = int(max_bytes_raw)
        except (TypeError, ValueError):
            return ToolResult.failure(error="max_bytes must be an integer")

        run_res = self._run_git(["show", rev], max_output_bytes=max_bytes)
        if run_res.exit_code != 0:
            return ToolResult.failure(
                error="git_show failed",
                output=json.dumps(
                    {
                        "type": "git_show",
                        "rev": rev,
                        "exit_code": run_res.exit_code,
                        "stdout": run_res.stdout,
                        "stderr": run_res.stderr,
                    },
                    ensure_ascii=False,
                ),
                metadata={"exit_code": run_res.exit_code, "stderr": run_res.stderr},
            )

        payload = {
            "type": "git_show",
            "rev": rev,
            "exit_code": run_res.exit_code,
            "stdout": run_res.stdout,
            "stderr": run_res.stderr,
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"exit_code": run_res.exit_code},
        )


def make_git_tools(repo_root: str | Path) -> list[BaseTool]:
    """Convenience factory to register git tools."""

    return [
        GitStatusTool(repo_root=repo_root),
        GitDiffTool(repo_root=repo_root),
        GitLogTool(repo_root=repo_root),
        GitShowTool(repo_root=repo_root),
    ]
