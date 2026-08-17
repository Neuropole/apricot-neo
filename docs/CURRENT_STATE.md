# Apricot Neo: Current Implementation State

## 1. Executive Summary

Apricot Neo is in **Phase 0 (Greenfield Baseline)**. The repository contains foundational manifests, git configuration, and vision documentation, but **no active application code, CLI, agent runtime, or backend services exist yet**.

---

## 2. Capability Matrix

| System / Capability | Status | Evidence / Notes |
| :--- | :--- | :--- |
| **Dependency Declarations** | Working | [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt) defines key libraries (`groq`, `chromadb`, `tree-sitter`, `PyGithub`, etc.) |
| **Git Configuration** | Working | [`.gitignore`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.gitignore) ignores standard Python artifacts, virtual environments, `.agent/` cache, embeddings, and vector DBs. |
| **Documentation & Vision** | Working | [`docs/neo-aprct-context.md`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md) outlines the Apricot 2.0 master plan. |
| **Agent Runtime & Execution Loop** | **Does Not Exist** | No Python runtime files or modules (`src/`, `apricot/`) exist. |
| **LLM Provider Abstraction** | **Does Not Exist** | Only library reference `groq` in [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt#L9). |
| **Repository Brain / Indexing** | **Does Not Exist** | No AST parsing, graph generation, or ChromaDB indexing logic implemented. |
| **Tool Registry & Execution** | **Does Not Exist** | No tool definitions (file read/write, bash execution, git tools) present. |
| **GitHub Integration / Webhooks** | **Does Not Exist** | No GitHub App, webhook endpoints, or PyGithub API wrappers written. |
| **CLI / Interface** | **Does Not Exist** | No CLI scripts (e.g. using `click` or `rich`) created. |
| **Test Suite / Automation** | **Does Not Exist** | No `tests/` directory or test runner configuration (e.g., `pytest`). |
| **CI / CD Pipelines** | **Does Not Exist** | No `.github/workflows/` directory. |

---

## 3. What Currently Works
* **Dependency installation baseline:** Dependencies can be installed using `pip install -r requirements.txt`.
* **Git ignore rules:** Prevents committing `.env`, virtualenvs, credentials, cached embeddings, and runtime databases.

---

## 4. What Partially Works
* **Project Specifications:** Product vision and requirements are documented in [`docs/neo-aprct-context.md`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md), but architectural implementation specifications and API contracts have yet to be materialized in code.

---

## 5. What Does Not Exist
* **No package structure:** No `pyproject.toml`, `setup.py`, or `src/` directory.
* **No Agent Runtime:** No core loop, prompt templates, context manager, or execution tools.
* **No Repository Brain:** No code parser, relationship graph, or ChromaDB vector store wrapper.
* **No Planner:** No reasoning, replanning, or specialized investigator agents.
* **No Review / Implementation Engine:** No diff generation, autonomous editing, or self-review engine.
* **No GitHub Integration:** No bot identity, webhook handlers, or PR automation.
* **No Web UI or API:** No frontend dashboard, API server, or background task queue.

---

## 6. Current Technical Debt & Risks

1. **Unpinned Dependency Versions:**
   * In [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt), all dependencies (`groq`, `chromadb`, `tree-sitter`, `sentence-transformers`, `PyGithub`, etc.) lack pinned versions. This creates a risk of non-deterministic builds or breaking upstream changes (especially in rapidly changing libraries like `tree-sitter` and `chromadb`).
2. **Lack of Standard Packaging / Modern Tooling:**
   * No `pyproject.toml` (PEP 517/621) configuration or environment locking (`uv`, `poetry`, or `pip-tools`).
3. **No Testing or Quality Gates:**
   * No test suite (`pytest`), linter/formatter (`ruff`), or static typechecker (`mypy`) configured.
4. **Platform Compatibility for Parsers:**
   * `tree-sitter` native grammar bindings require C compilation or prebuilt binary wheels across target operating systems (Windows, Linux, macOS).
