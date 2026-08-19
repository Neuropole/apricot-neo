"""Repository inspection tools for Phase 1.3.

These tools operate strictly inside an explicitly configured repository root.
They prevent directory traversal outside that root and avoid loading huge/binary
files unnecessarily.
"""

from __future__ import annotations

import json
import os
import re
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apricot.tools.base import BaseTool, ToolResult

# Exclusions are intentionally conservative: skip common VCS metadata, virtual envs,
# caches, and generated artifacts.
EXCLUDED_DIRS: set[str] = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".idea",
    ".vscode",
    "node_modules",
    "dist",
    "build",
    "coverage",
    ".eggs",
}

EXCLUDED_SUFFIXES: set[str] = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".class",
    ".jar",
    ".war",
    ".ear",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".webp",
    ".exe",
    ".msi",
}


CODE_EXTENSIONS: set[str] = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".kt",
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hpp",
    ".rs",
    ".go",
    ".rb",
    ".php",
    ".cs",
    ".swift",
    ".m",
    ".mm",
    ".sql",
    ".sh",
    ".ps1",
    ".yml",
    ".yaml",
    ".toml",
    ".json",
    ".env",
    ".mdown",
}


@dataclass(frozen=True)
class _ResolvedPath:
    abs_path: Path
    rel_path: Path


class RepoSandboxError(ValueError):
    """Raised when user-provided paths fail sandboxing checks."""


class RepoSandbox:
    """Shared path resolution + exclusions."""

    def __init__(self, repo_root: str | Path) -> None:
        self._repo_root = Path(repo_root).resolve(strict=False)

    @property
    def repo_root(self) -> Path:
        return self._repo_root

    def _ensure_valid_root(self) -> None:
        if not self._repo_root.is_dir():
            raise RepoSandboxError(f"Repository root is not a directory: '{self._repo_root}'")

    @staticmethod
    def _normalize_rel_path(rel_path: str) -> str:
        # Normalize separators and reject obviously invalid values early.
        if "\x00" in rel_path:
            raise RepoSandboxError("Path contains NUL byte")
        # LLMs sometimes send absolute-like paths; those are rejected.
        if Path(rel_path).is_absolute():
            raise RepoSandboxError("Absolute paths are not allowed")
        # Reject direct traversal tokens.
        parts = Path(rel_path).parts
        if any(p in ("..",) for p in parts):
            raise RepoSandboxError("Path traversal outside repository is not allowed")
        return rel_path.replace("\\", "/").lstrip("./")

    def resolve_within_repo(self, rel_path: str) -> _ResolvedPath:
        """Resolve a relative path (inside the repo) with traversal protection."""

        self._ensure_valid_root()
        normalized = self._normalize_rel_path(rel_path)

        # Empty means "repo root"
        rel = Path(normalized) if normalized else Path()
        abs_candidate = (self._repo_root / rel).resolve(strict=False)

        try:
            rel_check = abs_candidate.relative_to(self._repo_root)
        except ValueError as exc:
            raise RepoSandboxError("Requested path is outside the repository boundary") from exc

        return _ResolvedPath(abs_path=abs_candidate, rel_path=rel_check)

    def _is_excluded_dir(self, dir_name: str) -> bool:
        return dir_name in EXCLUDED_DIRS

    def _is_excluded_suffix(self, file_name: str) -> bool:
        suffix = Path(file_name).suffix.lower()
        return suffix in EXCLUDED_SUFFIXES

    def is_excluded_path(self, path: Path) -> bool:
        """Return whether a path contains a directory/file excluded from inspection."""
        try:
            rel_parts = path.relative_to(self._repo_root).parts
        except ValueError:
            return True
        return any(part in EXCLUDED_DIRS for part in rel_parts) or (
            bool(rel_parts) and self._is_excluded_suffix(rel_parts[-1])
        )

    def iter_files(
        self,
        start: Path,
        *,
        recursive: bool,
        max_files: int,
        code_only: bool,
    ) -> Iterable[Path]:
        """Yield absolute file paths under repo, respecting exclusions."""

        if max_files <= 0:
            return

        start_abs = start
        if not start_abs.exists():
            return

        if start_abs.is_file():
            if code_only:
                if start_abs.suffix.lower() not in CODE_EXTENSIONS:
                    return
            if self._is_excluded_suffix(start_abs.name):
                return
            # Prevent symlink escape: only yield if the resolved target stays within repo_root.
            try:
                start_abs.resolve(strict=False).relative_to(self._repo_root)
            except ValueError:
                return
            yield start_abs
            return

        # Directory walking (streaming, no large memory loads).
        if recursive:
            for root, dirs, files in os.walk(start_abs):
                # Modify dirs in place to prune.
                dirs[:] = [d for d in dirs if not self._is_excluded_dir(d)]
                for fn in files:
                    path_abs = Path(root) / fn
                    if self._is_excluded_suffix(fn):
                        continue
                    if code_only and path_abs.suffix.lower() not in CODE_EXTENSIONS:
                        continue
                    # Prevent symlink escape: resolved target must stay within repo_root.
                    try:
                        path_abs.resolve(strict=False).relative_to(self._repo_root)
                    except ValueError:
                        continue
                    yield path_abs
        else:
            try:
                for child in start_abs.iterdir():
                    if child.is_dir():
                        if self._is_excluded_dir(child.name):
                            continue
                        continue
                    if self._is_excluded_suffix(child.name):
                        continue
                    if code_only and child.suffix.lower() not in CODE_EXTENSIONS:
                        continue
                    # Prevent symlink escape: resolved target must stay within repo_root.
                    try:
                        child.resolve(strict=False).relative_to(self._repo_root)
                    except ValueError:
                        continue
                    yield child
            except OSError:
                return


def _looks_like_binary(sample: bytes) -> bool:
    if b"\x00" in sample:
        return True
    try:
        sample.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def _read_text_limited(abs_path: Path, *, max_bytes: int) -> tuple[str, dict[str, Any]]:
    """Read a text file up to max_bytes. Raises on binary."""

    st = abs_path.stat()
    size = st.st_size

    # Avoid huge memory loads.
    read_cap = max_bytes if size > max_bytes else size
    with abs_path.open("rb") as f:
        sample = f.read(min(4096, read_cap))
        if _looks_like_binary(sample):
            raise ValueError("Binary file not supported")

        f.seek(0)
        data = f.read(read_cap)

    # Replace invalid sequences rather than throwing; we already rejected obvious binaries.
    text = data.decode("utf-8", errors="replace")
    truncated = size > read_cap

    # Heuristic: if too many replacement chars, likely not proper UTF-8.
    replacement_ratio: float = 0.0
    if len(text) > 0:
        replacement_ratio = text.count("\ufffd") / len(text)
    metadata: dict[str, Any] = {
        "size_bytes": size,
        "read_bytes": len(data),
        "truncated": truncated,
        "replacement_ratio": replacement_ratio,
    }

    return text, metadata


class ListFilesTool(BaseTool):
    """List files under a repository folder."""

    def __init__(self, repo_root: str | Path) -> None:
        self._sandbox = RepoSandbox(repo_root)

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List repository files within a sandboxed root (excludes .git and caches)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Repo-relative dir; '' = root.",
                },
                "recursive": {"type": "boolean", "description": "Whether to walk subdirectories."},
                "max_files": {"type": "integer", "description": "Upper bound on returned files."},
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        path_raw = kwargs.get("path", "")
        path = path_raw if isinstance(path_raw, str) else str(path_raw)

        recursive_raw = kwargs.get("recursive", True)
        recursive = recursive_raw if isinstance(recursive_raw, bool) else bool(recursive_raw)

        max_files_raw = kwargs.get("max_files", 2000)
        try:
            max_files = int(max_files_raw)
        except (TypeError, ValueError):
            return ToolResult.failure(error="max_files must be an integer")
        if max_files <= 0:
            return ToolResult.failure(error="max_files must be greater than zero")

        try:
            resolved = self._sandbox.resolve_within_repo(path)
        except RepoSandboxError as exc:
            return ToolResult.failure(error=str(exc))

        abs_path = resolved.abs_path
        if self._sandbox.is_excluded_path(abs_path):
            return ToolResult.failure(error="Requested path is excluded from repository inspection")
        if not abs_path.exists():
            return ToolResult.failure(error="Requested path does not exist")

        entries: list[dict[str, Any]] = []

        def add_entry(p: Path) -> None:
            if len(entries) >= max_files:
                return
            try:
                rel = p.relative_to(self._sandbox.repo_root).as_posix()
            except ValueError:
                # Shouldn't happen due to sandboxing, but keep safe.
                return

            try:
                st = p.stat()
                size = st.st_size
                mtime = st.st_mtime
            except OSError:
                size = None
                mtime = None

            entries.append({"path": rel, "size": size, "mtime": mtime})

        if abs_path.is_file():
            add_entry(abs_path)
        else:
            for f_abs in self._sandbox.iter_files(
                abs_path, recursive=recursive, max_files=max_files, code_only=False
            ):
                add_entry(f_abs)
                if len(entries) >= max_files:
                    break

        payload = {
            "type": "list_files",
            "repo_root": self._sandbox.repo_root.as_posix(),
            "requested_path": path,
            "count": len(entries),
            "entries": entries,
        }
        return ToolResult.ok(output=json.dumps(payload, ensure_ascii=False))


class ReadFileTool(BaseTool):
    """Read a text file from the repository sandbox."""

    def __init__(self, repo_root: str | Path) -> None:
        self._sandbox = RepoSandbox(repo_root)

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return "Read a UTF-8 text file from the repository (rejects binaries, enforces sandbox)."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Repo-relative file path."},
                "max_bytes": {
                    "type": "integer",
                    "description": "Maximum number of bytes to read (truncates large files).",
                },
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        path_raw = kwargs.get("path")
        if not isinstance(path_raw, str) or not path_raw:
            return ToolResult.failure(error="path must be a non-empty string")
        path = path_raw

        max_bytes_raw = kwargs.get("max_bytes", 200_000)
        try:
            max_bytes = int(max_bytes_raw)
        except (TypeError, ValueError):
            return ToolResult.failure(error="max_bytes must be an integer")
        if max_bytes <= 0:
            return ToolResult.failure(error="max_bytes must be greater than zero")

        try:
            resolved = self._sandbox.resolve_within_repo(path)
        except RepoSandboxError as exc:
            return ToolResult.failure(error=str(exc))

        abs_path = resolved.abs_path
        if self._sandbox.is_excluded_path(abs_path):
            return ToolResult.failure(error="Requested path is excluded from repository inspection")
        if not abs_path.exists():
            return ToolResult.failure(error="File does not exist")
        if not abs_path.is_file():
            return ToolResult.failure(error="Requested path is not a file")

        # Reject special devices.
        mode = abs_path.stat().st_mode
        if stat.S_ISDIR(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISFIFO(mode):
            return ToolResult.failure(error="Requested path is not a regular file")

        try:
            text, meta = _read_text_limited(abs_path, max_bytes=max_bytes)
        except ValueError as exc:
            return ToolResult.failure(error=str(exc))
        except OSError as exc:
            return ToolResult.failure(error=f"Failed to read file: {exc}")

        payload = {
            "type": "read_file",
            "path": resolved.rel_path.as_posix(),
            "content": text,
            "metadata": meta,
        }
        return ToolResult.ok(output=json.dumps(payload, ensure_ascii=False), metadata=meta)


class _BaseSearchTool(BaseTool):
    """Shared implementation for search_* tools."""

    def __init__(self, repo_root: str | Path) -> None:
        self._sandbox = RepoSandbox(repo_root)

    def _validate_query(self, query: str) -> str | None:
        if query is None:
            return None
        stripped = query.strip()
        if not stripped:
            return None
        return stripped

    def _iter_search_files(
        self, start_abs: Path, *, recursive: bool, max_files: int, code_only: bool
    ) -> list[Path]:
        # Bound results; don't materialize huge lists (list is at most max_files).
        files: list[Path] = []
        for f_abs in self._sandbox.iter_files(
            start_abs, recursive=recursive, max_files=max_files, code_only=code_only
        ):
            files.append(f_abs)
            if len(files) >= max_files:
                break
        return files


class SearchTextTool(_BaseSearchTool):
    """Substring search across text files in the repository."""

    def __init__(self, repo_root: str | Path) -> None:
        super().__init__(repo_root)

    @property
    def name(self) -> str:
        return "search_text"

    @property
    def description(self) -> str:
        return "Search for a text substring inside UTF-8 files under the repository sandbox."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Substring to search for."},
                "path": {"type": "string", "description": "Repo-relative dir/file; '' = root."},
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive search.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max matches to return.",
                },
                "max_files": {
                    "type": "integer",
                    "description": "Max files to scan.",
                },
                "max_file_bytes": {
                    "type": "integer",
                    "description": "Skip files larger than this size.",
                },
                "max_preview_chars": {
                    "type": "integer",
                    "description": "Preview chars.",
                },
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query_raw = kwargs.get("query")
        if not isinstance(query_raw, str):
            return ToolResult.failure(error="query must be a string")
        query = query_raw

        path_raw = kwargs.get("path", "")
        path = path_raw if isinstance(path_raw, str) else str(path_raw)

        case_sensitive_raw = kwargs.get("case_sensitive", False)
        case_sensitive = (
            case_sensitive_raw
            if isinstance(case_sensitive_raw, bool)
            else bool(case_sensitive_raw)
        )

        try:
            max_results = int(kwargs.get("max_results", 50))
            max_files = int(kwargs.get("max_files", 500))
            max_file_bytes = int(kwargs.get("max_file_bytes", 1_500_000))
            max_preview_chars = int(kwargs.get("max_preview_chars", 220))
        except (TypeError, ValueError):
            return ToolResult.failure(error="numeric search parameters must be integers")
        if min(max_results, max_files, max_file_bytes, max_preview_chars) <= 0:
            return ToolResult.failure(error="search limits must be greater than zero")

        valid_query = self._validate_query(query)
        if valid_query is None:
            return ToolResult.failure(error="query must be a non-empty string")

        try:
            resolved = self._sandbox.resolve_within_repo(path)
        except RepoSandboxError as exc:
            return ToolResult.failure(error=str(exc))

        start_abs = resolved.abs_path
        if self._sandbox.is_excluded_path(start_abs):
            return ToolResult.failure(error="Requested path is excluded from repository inspection")
        if not start_abs.exists():
            return ToolResult.failure(error="Requested search path does not exist")

        files = self._iter_search_files(
            start_abs, recursive=True, max_files=max_files, code_only=False
        )

        q_cmp = valid_query if case_sensitive else valid_query.lower()
        matches: list[dict[str, Any]] = []

        skipped_binary = 0
        scanned_files = 0
        for f_abs in files:
            try:
                size = f_abs.stat().st_size
            except OSError:
                continue
            if size > max_file_bytes:
                continue

            try:
                # Quick binary check using a small sample.
                with f_abs.open("rb") as bf:
                    sample = bf.read(4096)
                if _looks_like_binary(sample):
                    skipped_binary += 1
                    continue
            except OSError:
                continue

            scanned_files += 1
            try:
                with f_abs.open("rb") as f:
                    for idx, line in enumerate(f, start=1):
                        try:
                            decoded = line.decode("utf-8", errors="replace")
                        except Exception:
                            continue
                        hay = decoded if case_sensitive else decoded.lower()
                        if q_cmp in hay:
                            try:
                                rel = f_abs.relative_to(self._sandbox.repo_root).as_posix()
                            except ValueError:
                                rel = str(f_abs)
                            preview = decoded.strip().replace("\t", " ")
                            if len(preview) > max_preview_chars:
                                preview = preview[:max_preview_chars] + "…"
                            matches.append(
                                {
                                    "path": rel,
                                    "line_number": idx,
                                    "preview": preview,
                                }
                            )
                            if len(matches) >= max_results:
                                break
                        if len(matches) >= max_results:
                            break
            except OSError:
                continue

            if len(matches) >= max_results:
                break

        payload = {
            "type": "search_text",
            "query": valid_query,
            "requested_path": path,
            "case_sensitive": case_sensitive,
            "matches": matches,
            "stats": {
                "files_scanned": scanned_files,
                "files_considered": len(files),
                "binary_skipped": skipped_binary,
                "max_results": max_results,
            },
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"matches": len(matches)},
        )


class SearchCodeTool(_BaseSearchTool):
    """Substring/regex search restricted to likely code files."""

    def __init__(self, repo_root: str | Path) -> None:
        super().__init__(repo_root)

    @property
    def name(self) -> str:
        return "search_code"

    @property
    def description(self) -> str:
        return "Search in likely code files under the repository sandbox."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Substring or regex pattern to search."},
                "path": {"type": "string", "description": "Repo-relative dir/file; '' = root."},
                "case_sensitive": {
                    "type": "boolean",
                    "description": "Case sensitive matching.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Max matches to return.",
                },
                "max_files": {
                    "type": "integer",
                    "description": "Max files to scan.",
                },
                "max_file_bytes": {
                    "type": "integer",
                    "description": "Skip files larger than this size.",
                },
                "max_preview_chars": {
                    "type": "integer",
                    "description": "Preview chars.",
                },
                "use_regex": {
                    "type": "boolean",
                    "description": "Treat query as a regex pattern.",
                },
            },
        }

    def execute(self, **kwargs: Any) -> ToolResult:
        query_raw = kwargs.get("query")
        if not isinstance(query_raw, str):
            return ToolResult.failure(error="query must be a string")
        query = query_raw

        path_raw = kwargs.get("path", "")
        path = path_raw if isinstance(path_raw, str) else str(path_raw)

        case_sensitive_raw = kwargs.get("case_sensitive", False)
        case_sensitive = (
            case_sensitive_raw
            if isinstance(case_sensitive_raw, bool)
            else bool(case_sensitive_raw)
        )

        use_regex_raw = kwargs.get("use_regex", False)
        use_regex = use_regex_raw if isinstance(use_regex_raw, bool) else bool(use_regex_raw)

        try:
            max_results = int(kwargs.get("max_results", 50))
            max_files = int(kwargs.get("max_files", 500))
            max_file_bytes = int(kwargs.get("max_file_bytes", 1_500_000))
            max_preview_chars = int(kwargs.get("max_preview_chars", 220))
        except (TypeError, ValueError):
            return ToolResult.failure(error="numeric search parameters must be integers")
        if min(max_results, max_files, max_file_bytes, max_preview_chars) <= 0:
            return ToolResult.failure(error="search limits must be greater than zero")

        valid_query = self._validate_query(query)
        if valid_query is None:
            return ToolResult.failure(error="query must be a non-empty string")

        try:
            resolved = self._sandbox.resolve_within_repo(path)
        except RepoSandboxError as exc:
            return ToolResult.failure(error=str(exc))

        start_abs = resolved.abs_path
        if self._sandbox.is_excluded_path(start_abs):
            return ToolResult.failure(error="Requested path is excluded from repository inspection")
        if not start_abs.exists():
            return ToolResult.failure(error="Requested search path does not exist")

        pattern: re.Pattern[str] | None = None
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                pattern = re.compile(valid_query, flags=flags)
            except re.error as exc:
                return ToolResult.failure(error=f"Invalid regex: {exc}")
        q_cmp = valid_query if case_sensitive else valid_query.lower()

        files = self._iter_search_files(
            start_abs, recursive=True, max_files=max_files, code_only=True
        )

        matches: list[dict[str, Any]] = []
        skipped_binary = 0
        scanned_files = 0
        for f_abs in files:
            try:
                size = f_abs.stat().st_size
            except OSError:
                continue
            if size > max_file_bytes:
                continue

            try:
                with f_abs.open("rb") as bf:
                    sample = bf.read(4096)
                if _looks_like_binary(sample):
                    skipped_binary += 1
                    continue
            except OSError:
                continue

            scanned_files += 1
            try:
                with f_abs.open("rb") as f:
                    for idx, line in enumerate(f, start=1):
                        try:
                            decoded = line.decode("utf-8", errors="replace")
                        except Exception:
                            continue

                        if use_regex and pattern is not None:
                            is_match = bool(pattern.search(decoded))
                        else:
                            hay = decoded if case_sensitive else decoded.lower()
                            is_match = q_cmp in hay

                        if is_match:
                            try:
                                rel = f_abs.relative_to(self._sandbox.repo_root).as_posix()
                            except ValueError:
                                rel = str(f_abs)
                            preview = decoded.strip().replace("\t", " ")
                            if len(preview) > max_preview_chars:
                                preview = preview[:max_preview_chars] + "…"
                            matches.append(
                                {
                                    "path": rel,
                                    "line_number": idx,
                                    "preview": preview,
                                }
                            )
                            if len(matches) >= max_results:
                                break
                        if len(matches) >= max_results:
                            break
            except OSError:
                continue

            if len(matches) >= max_results:
                break

        payload = {
            "type": "search_code",
            "query": valid_query,
            "requested_path": path,
            "case_sensitive": case_sensitive,
            "use_regex": use_regex,
            "matches": matches,
            "stats": {
                "files_scanned": scanned_files,
                "files_considered": len(files),
                "binary_skipped": skipped_binary,
                "max_results": max_results,
            },
        }
        return ToolResult.ok(
            output=json.dumps(payload, ensure_ascii=False),
            metadata={"matches": len(matches)},
        )


def make_repository_tools(repo_root: str | Path) -> list[BaseTool]:
    """Convenience factory to register repository tools."""

    return [
        ListFilesTool(repo_root=repo_root),
        ReadFileTool(repo_root=repo_root),
        SearchTextTool(repo_root=repo_root),
        SearchCodeTool(repo_root=repo_root),
    ]
