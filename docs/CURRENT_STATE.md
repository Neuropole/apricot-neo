# Apricot Neo: Current Implementation State

## 1. Executive Summary

Apricot Neo has **completed Phase 0 (Baseline & Foundation)**. The repository contains a standard `pyproject.toml` packaging setup, `uv.lock`, minimal package skeleton in `src/apricot/`, smoke test suite in `tests/`, strict quality gates (`ruff`, `mypy`), environment template (`.env.example`), and CI automation (`.github/workflows/ci.yml`). 

The project is now entering **Phase 1: Agent Runtime**.

---

## 2. Capability Matrix

| System / Capability | Status | Evidence / Notes |
| :--- | :--- | :--- |
| **Dependency Declarations & Locking** | Working | [`pyproject.toml`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/pyproject.toml) and [`uv.lock`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/uv.lock) define and lock all runtime and dev dependencies. |
| **Git Configuration** | Working | [`.gitignore`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.gitignore) ignores standard Python artifacts, virtual environments, caches, and vector DBs. |
| **Environment Configuration** | Working | [`.env.example`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.env.example) template provided. |
| **Test Suite / Automation** | Working | Unit tests in `tests/unit/` and smoke tests in `tests/` passing under `pytest`. |
| **Linting & Type Checking** | Working | `ruff` and `mypy` (strict) passing with zero errors. |
| **CI / CD Pipelines** | Working | [`.github/workflows/ci.yml`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.github/workflows/ci.yml) matrix workflow across Python 3.10–3.13. |
| **LLM Provider Abstraction** | Working | [`src/apricot/models/base.py`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/src/apricot/models/base.py) & [`src/apricot/models/groq.py`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/src/apricot/models/groq.py). |
| **Tool System & Registry** | Working | [`src/apricot/tools/base.py`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/src/apricot/tools/base.py) (`BaseTool`, `FunctionTool`, `ToolRegistry`, `ToolResult`). |
| **Agent Runtime Loop & State** | Working | [`src/apricot/agent/runtime.py`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/src/apricot/agent/runtime.py) & [`src/apricot/agent/state.py`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/src/apricot/agent/state.py). |
| **Repository Brain / Indexing** | **Does Not Exist** | No AST parsing, graph generation, or ChromaDB indexing logic implemented yet. |
| **Built-in Coding Tools (FS/Git/Exec)** | **Does Not Exist** | Real filesystem/shell/git tools to be added in Phase 1.3. |
| **GitHub Integration / Webhooks** | **Does Not Exist** | No GitHub App, webhook endpoints, or PyGithub API wrappers written yet. |
| **CLI / Interface** | **Does Not Exist** | No CLI scripts (e.g. using `click` or `rich`) created yet. |

---

## 3. What Currently Works
* **Python Packaging & Locking:** Standard `pyproject.toml` managed with `uv` (`uv.lock`).
* **Model Abstraction:** Universal message models, provider interface, and `GroqProvider` with tool-calling support.
* **Tool Registry:** Tool registration, validation, schema generation, and safe execution dispatch.
* **Agent Runtime Loop:** Model -> Tool -> Execution -> Model iteration loop with state tracking, error resilience, and step limits.
* **Test & Quality Gates:** 33 unit and smoke tests passing under `pytest`, strict `mypy`, and `ruff`.

---

## 4. What Partially Works
* **Agent Capabilities:** The core agent loop and tool dispatch work, but currently operate on test/dummy tools until built-in filesystem, shell, and git tools are implemented in Phase 1.3.

---

## 5. What Does Not Exist
* **No Built-in Tools:** Real filesystem (`read_file`, `write_file`, `list_files`), git (`git_status`, `git_diff`), and execution (`run_command`) tools.
* **No Repository Brain:** No code parser, relationship graph, or ChromaDB vector store wrapper.
* **No Planner:** No reasoning, replanning, or specialized investigator agents.
* **No Review / Implementation Engine:** No diff generation, autonomous editing, or self-review engine.
* **No GitHub Integration:** No bot identity, webhook handlers, or PR automation.
* **No Web UI or CLI:** No user-facing CLI or web interface yet.

---

## 6. Current Technical Debt & Risks

1. **Tree-Sitter Platform Grammars:**
   * Platform-specific grammar wheels and parser loading must be validated across target operating systems during Phase 2.
