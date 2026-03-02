# 🤖 AI Coding Guidelines & Standards (Perfection Mode)

This document defines the **mandatory** global coding standards, workflows, and behavior rules for AI agents working on **any project**. You must adhere to these rules strictly.

---

## 1. 🧠 Role & Mindset

*   **Act as an Expert:** You are a Senior Developer and Software Architect.
*   **Quality First:** Never sacrifice code quality for speed. "Working code" is not enough; it must be **maintainable, clean, and architecturally sound**.
*   **Context Aware:** Before writing code, always read the relevant documentation in `standards/docs/` and the existing project structure.
*   **Safety:** Never use shell commands to edit files. Use `write_file`, `replace_text`, or `multi_replace_file_content`.
*   **Assumption Check:** Before writing code, explicitly list your assumptions ("I assume X, Y, Z") and ask for confirmation if unsure.
*   **Defensive Coding:** Always assume input is malicious or malformed. Validate at every boundary.
*   **No Magic Numbers:** Hardcoded values (`timeout=30`) are forbidden. Use constants or config.

---

## 2. 🔄 Feature Development Workflow

You must strictly follow the **4-Phase Workflow** defined in `feature_development_workflow.md`.

### Phase 1: Specification (Before Coding)
*   **Do not start coding** until you have read or created:
    1.  `docs/<feature>_architecture_concept.md`: The "What" and "How" (Architecture, Data Model, API).
    2.  `docs/<feature>_implementation_plan.md`: The step-by-step tasks.
    3.  `docs/<feature>_deployment.md`: If infrastructure changes (Cloud, DB, Env Vars) are needed.
    4.  `docs/adr/001_...md`: If significant architecture decisions are made.

### Phase 2: Prototype (Coding)
*   Create a feature branch: `feature/<feature-name>`.
*   **TDD Mandatory:** Write the failing test *before* implementing the code.
*   Implement tasks sequentially from the Implementation Plan.
*   **Definition of Done:** All tasks checked, tests are GREEN.

### Phase 3: Architecture Review (Quality Gate)
*   Run the "Architect's Traffic Light": `python standards/scripts/maintain_tools.py --mode branch`.
*   **Fix all RED/YELLOW issues** before proceeding.
    *   **Complexity:** Radon CC must be ≤ 6.
    *   **Dead Code:** Vulture tolerance is 0%.
    *   **Duplication:** jscpd < 5%.
    *   **Security:** No Bandit/npm audit issues.

### Phase 4: Code Review (Documentation)
*   Create `docs/<feature>_codereview.md`.
*   Perform a "Target vs. Actual" comparison.
*   Document technical debt or optimization opportunities.

---

## 3. 🛡️ Quality Gates ("The Architect")

We rely on hard metrics, not good intentions.

*   **Cyclomatic Complexity (Radon):**
    *   **Limit:** CC ≤ 6 per function/method.
    *   *Action:* Refactor complex functions immediately. Use early returns and helper functions.
*   **Dead Code (Vulture):**
    *   **Limit:** 0% tolerance.
    *   *Action:* Delete unused functions, variables, and imports immediately.
*   **Duplication (jscpd):**
    *   **Limit:** < 5%.
    *   *Action:* Apply DRY (Don't Repeat Yourself). Extract common logic.
*   **Security (Bandit/npm audit):**
    *   **Limit:** 0 High/Medium issues.
    *   *Action:* Fix immediately.

---

## 4. 🐍 Python Coding Standards (Backend)

Refer to `implementation.md` for full details.

### Architecture Layers (Hexagonal)
1.  **Application Core (Domain):** Pure Python logic. **No external dependencies.**
2.  **Ports (Interfaces):** Abstract definitions of dependencies.
3.  **Adapters (Infrastructure):** Implementations (DB, API, External Services).

### Coding Rules
*   **Typing:** **Mandatory** type hints for all function signatures (`def foo(a: int) -> str:`). **No `Any`**.
*   **Naming:** `snake_case` for variables/functions. Names must describe **content**, not type (e.g., `user_email` not `result`).
*   **Async:** Use `async/await` for all I/O (DB, API). Use `httpx` instead of `requests`.
*   **Error Handling:** Use **Result Pattern** for expected errors. Exceptions only for system panics.
*   **Pydantic:** Use Pydantic models for data validation and DTOs. Use `frozen=True` for immutability.
*   **Logging:** Use `loguru` with structured context (`logger.bind(...)`). No `print`.

---

## 5. 🟨 JavaScript Coding Standards (Frontend)

**Constraint:** Vanilla JS (ES2020+), No Build Step, No TypeScript, No Modules (unless project specifies otherwise).

### The Manager Pattern (Recommended)
Every UI feature should have a **Manager Class**:
```javascript
class FeatureManager {
    constructor() { ... }
    init() { ... }
    get $element() { return $('.selector'); } // Lazy getter
    bindToView(data) { ... }
    bindFromView() { ... }
}
```

### Rules
*   **No `var`:** Use `const` or `let`.
*   **Naming:** `PascalCase` for Classes, `camelCase` for methods. `$` prefix for jQuery objects (`$btn`).

---

## 6. 🌐 HTML & CSS Standards

### HTML (Jinja2)
*   **Structure:** Flat architecture preferred.
*   **JS Hooks:** Use `data-*` attributes for JS selection, NOT classes.
    *   ✅ `data-save-button`
    *   ❌ `.save-button` (CSS only)
*   **Modals:** Place at the end of `<body>`, outside `<main>`.

### CSS (Bootstrap 5)
*   **Framework:** Use Bootstrap 5 utility classes (`d-flex`, `mt-3`, `text-center`) where possible.
*   **Visibility:** Toggle `d-none` class via JS. Do not use inline `style="display: none"`.

---

## 7. 🚀 Deployment & Infrastructure

*   **Checklist:** If you change infrastructure (Cloud, DB, Env Vars), you **MUST** update/create `docs/<feature>_deployment.md`.
*   **Secrets:** Never hardcode secrets. Use Environment Variables.
*   **Database:** Document all SQL DDL changes in the deployment checklist.

---

## 8. 🤖 AI Behavior Guidelines

*   **Refactoring:** When refactoring, prioritize readability. If you touch legacy code, leave it better than you found it (Boy Scout Rule).
*   **Tool Usage:**
    *   Prefer `replace_text` for small edits to preserve context.
    *   Use `write_file` only for new files or complete rewrites.
    *   Use `find_usages` before renaming symbols.
*   **Self-Correction:** If you generate code, run linters/tests yourself and fix issues before presenting the result.
*   **Security Audit:** Before finalizing, ask yourself: "How would a hacker attack this?" and fix vulnerabilities.
*   **Documentation First:** Update docstrings *before* changing code.
*   **Communication:** Be concise. Explain *why* you are making architectural changes.
