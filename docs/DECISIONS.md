# Apricot Neo: Architectural Decisions (ADR)

## 1. Existing Decisions (Discovered in Repository)

The following architectural decisions are established directly by the current codebase artifacts ([`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt), [`.gitignore`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.gitignore), [`LICENSE`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/LICENSE)):

* **ADR-001: Implementation Language is Python**
  * *Context:* Determined by Python package manifests and `.gitignore` file.
  * *Decision:* The core agent runtime and repository intelligence tooling will be written in Python.
* **ADR-002: Core Vector & Embedding Engine**
  * *Context:* Specified in [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt#L6-L8).
  * *Decision:* ChromaDB (`chromadb`) will serve as the local vector storage engine, combined with `sentence-transformers` for local embedding computation.
* **ADR-003: Code Parsing with Tree-Sitter**
  * *Context:* Specified in [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt#L7).
  * *Decision:* Concrete syntax tree (CST/AST) parsing and code symbol extraction will be handled via `tree-sitter`.
* **ADR-004: Primary Cloud LLM Inference Engine**
  * *Context:* Specified in [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt#L9).
  * *Decision:* Initial cloud inference will leverage Groq via the `groq` SDK.
* **ADR-005: CLI Framework**
  * *Context:* Specified in [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt#L4-L5).
  * *Decision:* `click` will be used for command-line parsing and `rich` for formatted terminal output.
* **ADR-006: Open Source Licensing**
  * *Context:* [`LICENSE`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/LICENSE).
  * *Decision:* Project is released under the permissive MIT License.

---

## 2. Proposed Decisions (From Apricot 2.0 Master Plan)

The following architectural directions are proposed in [`docs/neo-aprct-context.md`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md):

* **PROP-001: Dedicated Agent Runtime vs Third-Party CLI Harness**
  * *Proposal:* Build a specialized, custom Python agent runtime tailored for repository graph traversal and verification rather than wrapping external CLI tools.
* **PROP-002: Model Routing Strategy (Tiered Execution)**
  * *Proposal:* Route ~80-95% of tasks to cheap/local models (Ollama/Groq) and reserve frontier/strong models (~5-20%) for complex architecture reasoning, difficult debugging, or final verification.
* **PROP-003: GitHub App Architecture Over GitHub Actions**
  * *Proposal:* Build Apricot 2.0 as an autonomous GitHub bot / hosted service backed by a web application rather than being constrained to ephemeral GitHub Actions runners.
* **PROP-004: Evidence-First Findings & Self-Review**
  * *Proposal:* The agent must formulate hypotheses, trace dependency evidence, run targeted tests, and self-review before submitting PRs or review findings.

---

## 3. Apricot Neo Decisions Pending (Unresolved Decisions)

The following architectural and engineering decisions require resolution by human maintainers:

1. **Python Packaging Standard:**
   * *Status:* Unresolved.
   * *Options:* Migrate from raw `requirements.txt` to `pyproject.toml` using `hatchling`, `flit`, `setuptools`, or modern tooling like `uv` / `poetry`.
2. **Web Framework & Backend Stack:**
   * *Status:* Unresolved.
   * *Options:* FastAPI (Python) vs Next.js / TypeScript API server for the future web/webhook platform (Phase 6–7).
3. **Database & Task Queue Infrastructure for Hosting:**
   * *Status:* Unresolved.
   * *Options:* Postgres + Celery/Redis vs lightweight SQLite + background worker queue during early iterations.
4. **Tree-Sitter Grammar Distribution:**
   * *Status:* Unresolved.
   * *Options:* Explicitly install individual grammar packages (`tree-sitter-python`, `tree-sitter-javascript`, etc.) vs custom C compilation bindings.
5. **Execution Sandboxing Mechanism:**
   * *Status:* Unresolved.
   * *Options:* Docker containers vs Firecracker microVMs vs local sub-processes with strict path and command validation.
