# Apricot Neo Documentation Index

Welcome to the documentation suite for **Apricot Neo**. This directory is the authoritative context source for human engineers and AI coding agents working on the Apricot Neo codebase.

---

## 1. What is Apricot Neo?

Apricot Neo is an evolving repository-native autonomous GitHub software engineering agent. Unlike diff-only PR review tools or generic coding CLI wrappers, Apricot operates on a deep, connected understanding of the entire codebase (AST symbols, dependency call graphs, semantic vectors, git history, and test relationships) before planning, implementing, verifying, and reviewing software changes.

---

## 2. Where to Start Reading

To quickly get up to speed, read the documentation files in the following order:

1. [**`CURRENT_STATE.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/CURRENT_STATE.md): Understand what exists today versus what is planned.
2. [**`ARCHITECTURE.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/ARCHITECTURE.md): Learn the current baseline and target system architecture.
3. [**`REPOSITORY_MAP.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/REPOSITORY_MAP.md): Navigate existing files and planned source modules.
4. [**`AGENT_RUNTIME.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/AGENT_RUNTIME.md): Review the planned Phase 1 agent runtime specification.
5. [**`DEVELOPMENT.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/DEVELOPMENT.md): Learn environment setup and development guidelines.
6. [**`DECISIONS.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/DECISIONS.md): Review accepted ADRs and pending design decisions.
7. [**`ROADMAP.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/ROADMAP.md): View the phased delivery schedule from Phase 0 to Phase 8.
8. [**`neo-aprct-context.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md): Consult the original master plan for deeper product vision and design principles.

---

## 3. Authoritative Document Hierarchy

When discrepancies arise between documents, follow this hierarchy:
1. **Repository Reality / Codebase Files**: What is physically in the repo is absolute truth.
2. [**`CURRENT_STATE.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/CURRENT_STATE.md): Truth on implementation completeness.
3. [**`ARCHITECTURE.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/ARCHITECTURE.md) & [**`DECISIONS.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/DECISIONS.md): Architectural contracts and records.
4. [**`ROADMAP.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/ROADMAP.md): Phase planning and prerequisites.
5. [**`neo-aprct-context.md`**](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md): High-level product vision and inspiration.

---

## 4. Important Conventions

* **No Premature Feature Claims:** Never claim a component, tool, or system is implemented unless verified in source files.
* **Evidence-Driven Execution:** AI agents must formulate verifiable steps and test hypotheses against real code.
* **Modular Layering:** Maintain clean separation between the Agent Runtime, LLM Providers, Repository Brain, and Platform/GitHub connectors.

---

## 5. Agent Handoff

```text
================================================================================
APRICOT NEO AGENT HANDOFF
================================================================================

CURRENT SYSTEM:
- Phase 0 foundation complete.
- Packaging configured via pyproject.toml with dependencies locked in uv.lock.
- Clean package skeleton in src/apricot/ with subpackages (agent/, tools/, repository/, models/, github/, config/, utils/).
- Test suite configured (pytest) with smoke tests passing.
- Quality gates configured (ruff, strict mypy).
- Matrix CI workflow setup in .github/workflows/ci.yml and environment template in .env.example.

KNOWN GAPS:
- No Agent Runtime implementation (no LLM loop, tool registry, or provider interface).
- No Repository Brain implementation (no AST parsing, symbol indexing, or ChromaDB vector store).
- No Planner or specialized investigator agents.
- No CLI or web interfaces.

IMPORTANT FILES:
- pyproject.toml: Packaging metadata, dependency specs, and tool configs.
- uv.lock: Deterministic dependency lockfile.
- src/apricot/: Root package tree and namespace skeletons.
- tests/test_smoke.py: Smoke test suite.
- .github/workflows/ci.yml: Matrix CI workflow.
- .env.example: Environment variable template.
- docs/neo-aprct-context.md: Product master plan.
- docs/CURRENT_STATE.md: Exact capability audit.
- docs/ARCHITECTURE.md: Target architecture blueprints.
- docs/DECISIONS.md: Recorded ADRs and pending choices.
- docs/ROADMAP.md: Phased implementation guide.

CURRENT PHASE:
- Phase 1: Agent Runtime.

NEXT RECOMMENDED TASK:
- Phase 1.1: LLM Provider Abstraction & Client (src/apricot/models/base.py and initial GroqProvider implementation with tests).

UNRESOLVED DECISIONS:
- Selection of Python build backend / packaging standard (e.g. pyproject.toml with flit/hatchling/setuptools).
- Web backend framework selection (FastAPI vs TypeScript) for later phases.
- Task queue and worker infrastructure for hosted deployment.
- Tree-sitter grammar package management strategy.

RULES FOR FUTURE AGENTS:
1. Do not invent existing code; check repository reality first.
2. Ground all architecture decisions in docs/DECISIONS.md.
3. Keep Phase 1 (local agent runtime) focused and minimal before attempting repository graph or web layers.
4. Always accompany code changes with corresponding unit/integration tests.
================================================================================
```
