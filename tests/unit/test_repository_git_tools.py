from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from apricot.tools.git_tools import GitDiffTool, GitLogTool, GitShowTool, GitStatusTool
from apricot.tools.repository_tools import (
    ListFilesTool,
    ReadFileTool,
    SearchCodeTool,
    SearchTextTool,
)


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _require_git() -> None:
    proc = _run(["git", "--version"], cwd=Path.cwd())
    if proc.returncode != 0:
        pytest.skip("git executable not available")


def _init_git_repo(repo: Path) -> None:
    proc = _run(["git", "init", "-b", "main"], cwd=repo)
    if proc.returncode != 0:
        proc = _run(["git", "init"], cwd=repo)
    assert proc.returncode == 0, f"git init failed: {proc.stderr}"

    # Local commit identity and settings so `git commit` works cleanly in CI/test environments.
    _run(["git", "config", "user.email", "test@example.com"], cwd=repo).check_returncode()
    _run(["git", "config", "user.name", "Test User"], cwd=repo).check_returncode()
    _run(["git", "config", "commit.gpgsign", "false"], cwd=repo).check_returncode()
    _run(["git", "config", "core.hooksPath", ""], cwd=repo).check_returncode()


@pytest.fixture()
def repo_with_files(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "src").mkdir()
    (repo / "docs").mkdir()
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / "__pycache__").mkdir()
    (repo / ".git").mkdir()

    (repo / "src" / "example.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("hello world\n", encoding="utf-8")
    (repo / "docs" / "note.txt").write_text("this contains needle\n", encoding="utf-8")
    (repo / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
    (repo / ".env").write_text("SECRET_KEY=12345\n", encoding="utf-8")

    # Excluded dir content.
    (repo / ".git" / "secret.txt").write_text("should not show up\n", encoding="utf-8")
    (repo / "__pycache__" / "x.pyc").write_bytes(b"not real pyc but should be excluded")

    # Binary file for read_file safety checks.
    (repo / "bin.dat").write_bytes(b"\x00\x01\x02binary\xff")

    return repo


def test_list_files_and_read_file(repo_with_files: Path) -> None:
    tool = ListFilesTool(repo_root=repo_with_files)
    res = tool.execute(path="", recursive=True, max_files=200)
    assert res.success is True

    payload: dict[str, Any] = json.loads(res.output)
    entries: list[dict[str, Any]] = payload["entries"]
    paths = {e["path"] for e in entries}

    assert "src/example.py" in paths
    assert "README.md" in paths
    assert "docs/note.txt" in paths
    assert ".github/workflows/ci.yml" in paths
    assert "bin.dat" in paths
    # Excluded items
    assert ".env" not in paths
    assert not any(p == ".git" or p.startswith(".git/") or "/.git/" in p for p in paths)
    assert not any("secret.txt" in p for p in paths)

    read_tool = ReadFileTool(repo_root=repo_with_files)
    read_res = read_tool.execute(path="src/example.py", max_bytes=10_000)
    assert read_res.success is True
    read_payload: dict[str, Any] = json.loads(read_res.output)
    assert "def add" in read_payload["content"]

    # Test reading dot-directory file
    read_ci = read_tool.execute(path=".github/workflows/ci.yml")
    assert read_ci.success is True
    assert "name: CI" in json.loads(read_ci.output)["content"]


def test_path_traversal_is_rejected(repo_with_files: Path, tmp_path: Path) -> None:
    outside = tmp_path / "outside.txt"
    outside.write_text("outside\n", encoding="utf-8")

    tool = ReadFileTool(repo_root=repo_with_files)
    res = tool.execute(path="../outside.txt")
    assert res.success is False
    assert res.error is not None
    assert "outside repository boundary" in res.error or "Path traversal" in res.error

    list_tool = ListFilesTool(repo_root=repo_with_files)
    res_list = list_tool.execute(path="../outside.txt", recursive=False)
    assert res_list.success is False


def test_missing_and_invalid_paths(repo_with_files: Path) -> None:
    list_tool = ListFilesTool(repo_root=repo_with_files)
    res_list = list_tool.execute(path="missing_dir")
    assert res_list.success is False

    read_tool = ReadFileTool(repo_root=repo_with_files)
    res_read = read_tool.execute(path="missing.txt")
    assert res_read.success is False


def test_read_file_binary_rejected(repo_with_files: Path) -> None:
    tool = ReadFileTool(repo_root=repo_with_files)
    res = tool.execute(path="bin.dat", max_bytes=100_000)
    assert res.success is False
    assert res.error is not None
    assert "Binary file" in res.error


def test_excluded_paths_and_invalid_limits_are_rejected(repo_with_files: Path) -> None:
    read_tool = ReadFileTool(repo_root=repo_with_files)
    assert not read_tool.execute(path=".git/secret.txt").success
    assert not read_tool.execute(path=".env").success

    list_tool = ListFilesTool(repo_root=repo_with_files)
    assert not list_tool.execute(path=".git").success

    search_tool = SearchTextTool(repo_root=repo_with_files)
    assert not search_tool.execute(query="hello", max_results=0).success
    assert not read_tool.execute(path="README.md", max_bytes=0).success


def test_search_text_finds_substring(repo_with_files: Path) -> None:
    tool = SearchTextTool(repo_root=repo_with_files)
    res = tool.execute(query="needle", path="", case_sensitive=False, max_results=10)
    assert res.success is True
    payload: dict[str, Any] = json.loads(res.output)
    matches: list[dict[str, Any]] = payload["matches"]
    assert any(m["path"] == "docs/note.txt" for m in matches)

    # Search in dot-directory
    res_ci = tool.execute(query="name: CI", path=".github")
    assert res_ci.success is True
    assert any(
        m["path"] == ".github/workflows/ci.yml" for m in json.loads(res_ci.output)["matches"]
    )


def test_search_code_finds_code_only(repo_with_files: Path) -> None:
    tool = SearchCodeTool(repo_root=repo_with_files)
    res = tool.execute(query="def add", path="", case_sensitive=True, max_results=10)
    assert res.success is True
    payload: dict[str, Any] = json.loads(res.output)
    matches: list[dict[str, Any]] = payload["matches"]
    assert any(m["path"] == "src/example.py" for m in matches)


def test_search_code_regex_support(repo_with_files: Path) -> None:
    tool = SearchCodeTool(repo_root=repo_with_files)

    # Valid regex
    res = tool.execute(query=r"def\s+add\(a,\s*b\):", use_regex=True)
    assert res.success is True
    payload: dict[str, Any] = json.loads(res.output)
    assert any(m["path"] == "src/example.py" for m in payload["matches"])

    # Invalid regex pattern
    res_invalid = tool.execute(query=r"[invalid", use_regex=True)
    assert res_invalid.success is False
    assert "Invalid regex" in str(res_invalid.error)

    # Regex query exceeding max length
    res_long = tool.execute(query="a" * 501, use_regex=True)
    assert res_long.success is False
    assert "maximum length" in str(res_long.error)


def test_search_rejects_empty_query(repo_with_files: Path) -> None:
    tool = SearchTextTool(repo_root=repo_with_files)
    res = tool.execute(query="  ")
    assert res.success is False


def test_repository_boundary_enforcement_for_search(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.txt").write_text("hello\n", encoding="utf-8")

    outside = tmp_path / "outside.txt"
    outside.write_text("needle\n", encoding="utf-8")

    tool = SearchTextTool(repo_root=repo)
    res = tool.execute(query="needle", path="../outside.txt")
    assert res.success is False


def test_git_tools_happy_path(tmp_path: Path) -> None:
    _require_git()

    repo = tmp_path / "gitrepo"
    repo.mkdir()
    _init_git_repo(repo)

    (repo / "README.md").write_text("initial\n", encoding="utf-8")
    _run(["git", "add", "."], cwd=repo).check_returncode()
    proc1 = _run(["git", "commit", "-m", "initial commit"], cwd=repo)
    assert proc1.returncode == 0, proc1.stderr

    (repo / "README.md").write_text("initial\nsecond\n", encoding="utf-8")
    _run(["git", "add", "."], cwd=repo).check_returncode()
    proc2 = _run(["git", "commit", "-m", "second commit"], cwd=repo)
    assert proc2.returncode == 0, proc2.stderr

    # Uncommitted change to produce diffs + status.
    (repo / "README.md").write_text("initial\nsecond\nuncommitted change\n", encoding="utf-8")

    prev = _run(["git", "rev-parse", "HEAD~1"], cwd=repo)
    assert prev.returncode == 0
    prev_hash = prev.stdout.strip()

    status_tool = GitStatusTool(repo_root=repo)
    status_res = status_tool.execute()
    assert status_res.success is True
    status_payload: dict[str, Any] = json.loads(status_res.output)
    assert "README.md" in status_payload["stdout"]

    diff_tool = GitDiffTool(repo_root=repo)
    diff_res = diff_tool.execute(staged=False)
    assert diff_res.success is True
    diff_payload: dict[str, Any] = json.loads(diff_res.output)
    assert "uncommitted change" in diff_payload["stdout"]

    log_tool = GitLogTool(repo_root=repo)
    log_res = log_tool.execute(max_count=10)
    assert log_res.success is True
    log_payload: dict[str, Any] = json.loads(log_res.output)
    subjects = {c["subject"] for c in log_payload["commits"]}
    assert "initial commit" in subjects
    assert "second commit" in subjects

    show_tool = GitShowTool(repo_root=repo)
    show_res = show_tool.execute(rev=prev_hash)
    assert show_res.success is True
    show_payload: dict[str, Any] = json.loads(show_res.output)
    assert "initial commit" in show_payload["stdout"]


def test_git_tools_parameter_validation(tmp_path: Path) -> None:
    repo = tmp_path / "valid_repo"
    repo.mkdir()

    show_tool = GitShowTool(repo_root=repo)
    # Revisions starting with - are rejected
    assert show_tool.execute(rev="-p").success is False
    assert show_tool.execute(rev="").success is False
    assert show_tool.execute(rev="HEAD", max_bytes=0).success is False

    diff_tool = GitDiffTool(repo_root=repo)
    assert diff_tool.execute(max_bytes=0).success is False

    log_tool = GitLogTool(repo_root=repo)
    assert log_tool.execute(max_count=0).success is False
    assert log_tool.execute(max_count=1001).success is False
    assert log_tool.execute(max_bytes=-5).success is False


def test_git_tools_failure_handling_for_non_git_dir(tmp_path: Path) -> None:
    non_git = tmp_path / "not_a_repo"
    non_git.mkdir()

    status_tool = GitStatusTool(repo_root=non_git)
    res = status_tool.execute()
    assert res.success is False
    assert res.error is not None

    diff_tool = GitDiffTool(repo_root=non_git)
    res_diff = diff_tool.execute()
    assert res_diff.success is False

    log_tool = GitLogTool(repo_root=non_git)
    res_log = log_tool.execute()
    assert res_log.success is False

    show_tool = GitShowTool(repo_root=non_git)
    res_show = show_tool.execute(rev="HEAD")
    assert res_show.success is False


def test_git_tools_handle_invalid_root(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    assert GitStatusTool(repo_root=missing).execute().success is False
