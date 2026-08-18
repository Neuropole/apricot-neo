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

Using `uv` (recommended):
```bash
# Sync all runtime and dev dependencies
uv sync
```

Or using standard `pip`:
```bash
pip install --upgrade pip
pip install -e ".[dev]"
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
> Currently, the repository is in **Phase 0.5 (Foundation Skeleton)** and contains no CLI or server entry points. Running the project will become available once Phase 1 (`src/apricot/cli.py` or agent CLI) is implemented.

Target local execution command (Phase 1):
```bash
python -m apricot.cli --help
```

---

## 4. Testing & Code Quality

* **Testing:** `pytest`
  ```bash
  pytest
  ```
* **Linting & Formatting:** `ruff`
  ```bash
  ruff check .
  ruff format --check .
  ```
* **Type Checking:** `mypy`
  ```bash
  mypy
  ```

---

## 5. Technical Notes & Conventions

1. **Lockfile Management:**
   * Dependencies are pinned in `uv.lock` via `pyproject.toml`. Update with `uv lock` or `uv add <package>`.
2. **Tree-Sitter Grammars:**
   * Explicit language grammar packages (`tree-sitter-python`, `tree-sitter-javascript`, `tree-sitter-typescript`) are managed in `pyproject.toml`.
