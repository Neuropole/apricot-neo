# Apricot Neo: Development Guide

## 1. Prerequisites

* **Python:** 3.10+ recommended (due to modern type hinting and library support for Tree-sitter / ChromaDB).
* **Git:** Git 2.30+ installed and configured on the system.
* **API Keys:** A Groq API Key (`GROQ_API_KEY`) if testing cloud inference.

---

## 2. Environment Setup

### 2.1 Virtual Environment Creation

Create and activate an isolated Python virtual environment:

**On Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2.2 Installing Dependencies

Install current baseline dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Environment Configuration

Create a `.env` file in the repository root (ignored by [`.gitignore`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.gitignore)):
```dotenv
# LLM Providers
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional: Local / Future Settings
OLLAMA_BASE_URL=http://localhost:11434
APRICOT_LOG_LEVEL=INFO
```

---

## 3. Running Locally

> [!NOTE]
> Currently, the repository is in **Phase 0 (Greenfield)** and contains no CLI or server entry points. Running the project will become available once Phase 1 (`src/apricot/cli.py`) is implemented.

Target local execution command (Phase 1):
```bash
python -m apricot.cli --help
```

---

## 4. Testing & Code Quality (Recommended Setup)

While the repository does not yet include testing configurations, future agents and contributors should standardize on:

* **Testing:** `pytest`
  ```bash
  pytest tests/
  ```
* **Linting & Formatting:** `ruff`
  ```bash
  ruff check .
  ruff format --check .
  ```
* **Type Checking:** `mypy`
  ```bash
  mypy src/
  ```

---

## 5. Known Development Issues & Technical Notes

1. **Unpinned Dependencies in `requirements.txt`:**
   * Rapidly evolving packages (`chromadb`, `tree-sitter`, `sentence-transformers`) may introduce breaking changes on unpinned installs.
   * *Recommendation:* Adopt `pyproject.toml` or lockfiles (`uv.lock` or `pip-tools`) during Phase 0 stabilization.
2. **Tree-Sitter Language Grammars:**
   * In newer `tree-sitter` versions (0.22+), language grammar packages are separate wheels (e.g. `tree-sitter-python`, `tree-sitter-typescript`). They must be declared alongside `tree-sitter`.
3. **No Root Package Installed (`pip install -e .`):**
   * Without a `pyproject.toml` or `setup.py`, the repository cannot be installed in editable mode.
