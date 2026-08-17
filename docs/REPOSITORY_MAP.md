# Apricot Neo: Repository Map

## 1. Directory Structure

```text
apricot-neo/
├── .gitignore               # Standard Python, virtualenv, cache, and DB ignore patterns
├── LICENSE                  # MIT License
├── README.md                # Project header and summary
├── requirements.txt         # Core Python dependencies
└── docs/                    # Architectural and project documentation
    ├── README.md            # Entry point for AI coding agents and human contributors
    ├── ARCHITECTURE.md      # Current vs target system architecture
    ├── CURRENT_STATE.md     # Accurate audit of current implementation state
    ├── REPOSITORY_MAP.md    # This file: codebase navigation and module layout
    ├── AGENT_RUNTIME.md     # Agent runtime design and specifications
    ├── DEVELOPMENT.md       # Development instructions, setup, and testing guides
    ├── DECISIONS.md         # Architectural Decision Records (ADRs) & pending decisions
    ├── ROADMAP.md           # Phased evolution roadmap (Phase 0 to Phase 8)
    └── neo-aprct-context.md # Original master plan and product vision document
```

---

## 2. File Responsibilities (Current Files)

| File | Purpose & Responsibilities |
| :--- | :--- |
| [`.gitignore`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/.gitignore) | Configures ignore rules for Python bytecode (`__pycache__`), virtual environments (`.venv`, `venv`), secrets/environments (`.env`, `secrets.json`), temporary vector databases (`.agent_db/`), agent embedding caches (`.agent/embeddings/`), and coverage reports. |
| [`LICENSE`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/LICENSE) | MIT open-source license. |
| [`README.md`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/README.md) | High-level repository title and basic description. |
| [`requirements.txt`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/requirements.txt) | Inception dependencies: `requests`, `PyGithub`, `python-dotenv`, `click`, `rich`, `chromadb`, `tree-sitter`, `sentence-transformers`, `groq`. |
| [`docs/neo-aprct-context.md`](file:///C:/Users/hp/Desktop/PAPERS/neuropole/apricot-neo/docs/neo-aprct-context.md) | Authoritative product vision & design document for Apricot 2.0. |

---

## 3. Entry Points & Core Modules

* **Application Entry Points:** *None exist currently.* (Planned: CLI entry point via `click`/`rich` e.g., `src/apricot/cli.py`).
* **Core Modules:** *None exist currently.*
* **Test Suite:** *None exists currently.* (Planned: `tests/`).

---

## 4. Planned Source Layout (Target Phase 1 & 2 Structure)

To establish standard Python packaging as implementation begins, the recommended target directory layout is:

```text
src/
└── apricot/
    ├── __init__.py
    ├── cli.py               # CLI interface (Click / Rich)
    ├── config.py            # Settings & environment variables (.env)
    ├── core/                # Agent runtime & execution loop
    │   ├── agent.py         # Main agent loop & controller
    │   ├── context.py       # Context window management & budget compression
    │   └── history.py       # Message & execution step history
    ├── providers/           # LLM provider abstractions
    │   ├── base.py          # Abstract LLM provider interface
    │   ├── groq_provider.py # Groq API integration
    │   └── local_provider.py# Ollama / Local model integration
    ├── tools/               # Agent tool implementations
    │   ├── base.py          # Tool base class & registry
    │   ├── file_tools.py    # File read/write/list
    │   ├── git_tools.py     # Git status/diff/log/blame
    │   └── exec_tools.py    # Shell command & test execution
    └── brain/               # Repository intelligence (Phase 2)
        ├── parser.py        # Tree-sitter code parser
        ├── symbol_index.py  # Symbol table & references
        ├── vector_store.py  # ChromaDB embeddings integration
        └── graph.py         # Repository relationship graph
tests/
    ├── unit/                # Unit tests for tools, providers, parser
    ├── integration/         # Integration tests for agent loop
    └── fixtures/            # Sample code repos and fixtures for testing
```
