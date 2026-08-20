# Apricot Neo: Development Roadmap

This roadmap maps the master product plan ([`docs/neo-aprct-context.md`](neo-aprct-context.md)) against the current codebase state.

---

## 1. Roadmap Overview & Phase Status

```mermaid
gantt
    title Apricot Neo Phased Progression
    dateFormat  YYYY-MM-DD
    section Phases
    Phase 0: Baseline & Inception (Done)        :done, p0, 2026-08-01, 2026-08-18
    Phase 1: Agent Runtime (Complete)           :done, p1, 2026-08-18, 2026-08-20
    Phase 2: Repository Brain (Active)          :active, p2, 2026-08-20, 30d
    Phase 3: Planner                            :p3, after p2, 25d
    Phase 4: Autonomous Implementation          :p4, after p3, 30d
    Phase 5: High-Quality Code Review           :p5, after p4, 25d
    Phase 6: GitHub App Integration             :p6, after p5, 30d
    Phase 7: Web Application                   :p7, after p6, 35d
    Phase 8: Autonomous GitHub Engineer         :p8, after p7, 40d
```

| Phase | Description | Current Status | Prerequisites |
| :--- | :--- | :--- | :--- |
| **Phase 0** | Baseline & Cleanup | **COMPLETED** | Repository setup, packaging, CI/CD, documentation baseline. |
| **Phase 1** | Agent Runtime | **COMPLETED** | Completion of Phase 0 baseline & packaging. |
| **Phase 2** | Repository Brain | **ACTIVE** | Phase 1 (tool interface & execution loop). |
| **Phase 3** | Planner | **PLANNED** | Phase 1 (runtime) & Phase 2 (repository queries). |
| **Phase 4** | Autonomous Implementation | **PLANNED** | Phase 3 (planning & hypothesis testing). |
| **Phase 5** | High-Quality Code Review | **PLANNED** | Phase 2 (graph/AST) & Phase 3 (evidence engine). |
| **Phase 6** | GitHub App Integration | **PLANNED** | Phase 4 (autonomous changes) & Phase 5 (review). |
| **Phase 7** | Web Application | **PLANNED** | Phase 6 (bot webhooks and job queuing). |
| **Phase 8** | Autonomous GitHub Engineer | **PLANNED** | Full integration of all previous phases. |

---

## 2. Detailed Phase Breakdown

### Phase 0: Baseline and Cleanup (COMPLETED)
* **Objective:** Establish repo structure, packaging, development environment, and authoritative documentation.
* **Completed Deliverables:**
  * Authoritative architecture, state, decisions, and roadmap documentation in `docs/`.
  * Standard Python packaging via `pyproject.toml` and deterministic locking via `uv.lock`.
  * Minimal package skeleton (`src/apricot/` with 7 core subpackage namespaces).
  * Smoke test suite (`tests/test_smoke.py`) configured with `pytest`.
  * Strict code quality tooling (`ruff` and `mypy`).
  * Environment variable template (`.env.example`).
  * Automated GitHub Actions CI workflow (`.github/workflows/ci.yml`).

---

### Phase 1: Agent Runtime (COMPLETED)
* **Objective:** Turn Apricot into a functional, local, tool-using coding agent.
* **Completed Deliverables:**
  * Core agent ReAct iteration loop with `AgentState` and step limits.
  * Tool registry and base tool abstractions (`BaseTool`, `FunctionTool`, `ToolRegistry`, `ToolResult`).
  * Repository inspection tools (`list_files`, `read_file`, `search_text`, `search_code`) with sandboxing and exclusions.
  * Git inspection tools (`git_status`, `git_diff`, `git_log`, `git_show`) with safe subprocess handling.
  * Universal LLM provider abstraction with `GroqProvider` integration (Ollama deferred to Phase 2+).
  * Write tools (`write_file`) and shell/test execution tools deferred to subsequent execution phases.
* **Prerequisites:** Phase 0.

#### Phase 1.3: Repository & Git Tools (COMPLETED)
* **Objective:** Provide safe, provider-independent repository inspection and Git history tools for the Phase 1 agent.
* **Completed Deliverables:**
  * Repository-root-scoped `list_files`, `read_file`, `search_text`, and `search_code` tools.
  * Path traversal and symlink-boundary enforcement, exclusions for VCS metadata/caches/generated artifacts, binary detection, and bounded reads/searches.
  * Safe no-shell `git_status`, `git_diff`, `git_log`, and `git_show` tools with captured output, exit status, truncation, and failure handling.
  * Temporary repository tests covering normal operation, invalid paths, boundaries, searches, and Git failures.
* **Scope boundary:** Repository Brain indexing, embeddings, AST analysis, call graphs, and planners remain planned Phase 2+ work.

---

### Phase 2: Repository Brain
* **Objective:** Provide deep, multi-layered repository intelligence beyond diffs.
* **Target Deliverables:**
  * Tree-sitter AST symbol extractor (classes, functions, interfaces, imports).
  * Dependency relationship and call graph builder.
  * Semantic vector indexing using ChromaDB and Sentence-Transformers.
  * Test-to-code mapping and Git history awareness.
* **Prerequisites:** Phase 1.

---

### Phase 3: Planner
* **Objective:** Enable structured investigation, hypotheses generation, and replanning.
* **Target Deliverables:**
  * Task decomposition and investigation planner.
  * Dynamic replanning based on intermediate tool findings.
  * Evidence engine (distinguishing facts, hypotheses, observations, and proofs).
* **Prerequisites:** Phase 1 & Phase 2.

---

### Phase 4: Autonomous Implementation
* **Objective:** Enable the agent to locally solve issues and bugs end-to-end.
* **Target Deliverables:**
  * Multi-file patch generation and application.
  * Test reproduction loop (write test → reproduce bug → apply fix → verify).
  * Self-review pass before finalizing diff.
* **Prerequisites:** Phase 3.

---

### Phase 5: High-Quality Code Review
* **Objective:** Deliver deep repository-aware PR reviews with high signal-to-noise ratio.
* **Target Deliverables:**
  * Impact analysis and regression detection.
  * Evidence-backed review comments with verifiable test cases.
  * Confidence scoring to filter speculative comments.
* **Prerequisites:** Phase 2 & Phase 3.

---

### Phase 6: GitHub App Integration
* **Objective:** Transform Apricot into a real GitHub participant / bot.
* **Target Deliverables:**
  * GitHub App authentication and webhook handler.
  * Issue assignment ingestion, PR review triggers, and bot comments.
  * Automated git branching and PR creation via `PyGithub`.
* **Prerequisites:** Phase 4 & Phase 5.

---

### Phase 7: Web Application
* **Objective:** Provide a centralized dashboard and control plane for users.
* **Target Deliverables:**
  * Web interface for repository installation, task tracking, and run logs.
  * Execution state dashboard (showing evidence traces, files changed, test results).
  * User settings, model routing configs, and autonomy levels (Observe to Autonomous).
* **Prerequisites:** Phase 6.

---

### Phase 8: Autonomous GitHub Engineer
* **Objective:** Full autonomous GitHub workflow loop.
* **Target Deliverables:**
  * End-to-end autonomous issue handling, implementation, PR submission, and interactive comment addressing.
* **Prerequisites:** Phases 1 through 7.
