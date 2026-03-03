# Coding Standards for AI Agents (MANDATORY)

These rules MUST be followed during ALL code implementation. They are loaded automatically via `@import` in the project's CLAUDE.md.

---

## Python

Follow `standards/docs/implementation.md` for details. Key rules:

- Type hints mandatory (no `Any`), `snake_case` naming, line length 120
- CC ≤ 6 per function (use early returns, extract helpers)
- 0% dead code (remove unused imports, functions, variables immediately)
- Result Pattern for expected errors, Exceptions only for panics
- Repository pattern for DB access, async sessions with proper commit/rollback
- Google-style docstrings on public functions/classes
- `removeprefix()`/`removesuffix()` over `replace()` for prefix/suffix stripping
- Blocking I/O in async endpoints MUST use `run_in_executor` or `asyncio.to_thread`

## JavaScript

Follow `standards/docs/frontend_coding_guidelines.md` for details. Key rules:

- `'use strict';` + class-level JSDoc on every file
- DOM selectors as `static get SEL_*()` properties at class top (never hardcoded in methods)
- `data-*` attributes for JS hooks (not CSS classes, not IDs unless required by Bootstrap)
- All HTTP calls through `ApiService` (never raw `$.ajax` / `$.get`)
- No optimistic UI — always re-fetch after mutations
- `d-none` for visibility (no `.hide()`/`.show()` except for `slideUp`/`slideDown` animations)
- No native `alert()`/`confirm()` — use inline Bootstrap alerts
- Magic strings → `Object.freeze({...})` constants
- `Utils.escapeHtml()` on ALL user/API data injected into HTML
- API methods use options objects: `ApiService.get(url, { onSuccess, onError, params })`

## HTML / CSS

- Custom CSS only in `resources/css/custom.css`
- No inline `style` for JS-controlled behavior
- Bare `data-*` attributes (not `data-foo="true"`)
- Bootstrap 5 patterns, `role="button"` + `tabindex="0"` on clickable non-button elements
- `aria-label` on interactive elements without visible text

## SQL

- T-SQL dialect (Azure SQL Server)
- Lint with SQLFluff: `sqlfluff lint <file> --dialect tsql`

---

## Auto-Review & Quality Gate

### Tool Setup (once per session)
```bash
python standards/scripts/maintain_tools.py --setup
```

### Review Commands
```bash
# Review changes on current branch vs main
PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode branch

# Review uncommitted changes only
PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode commit
```

### Review-Fix Loop (after implementation)

After completing implementation work, run the `/review-fix` slash command or manually:

1. Run `PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode branch`
2. If Ampel is not GREEN: fix all findings **in the changed files only**
3. Re-run — repeat until GREEN or max 3 iterations
4. Report the final Ampel status to the user

### Toolchain
- **Python:** Ruff (Linter/Formatter), Vulture (Dead Code), Radon (Complexity)
- **JS/TS:** Biome (Lint/Format), Knip (Dead Code/Deps)
- **SQL:** SQLFluff (T-SQL Dialect)
- **HTML:** djLint
- **Duplicates:** jscpd (< 5%)

### Ampel Thresholds
- **GREEN:** No findings in changed files
- **YELLOW:** Complexity 10-19 (Radon CC rank C)
- **RED:** Complexity ≥ 20, or dead code, or duplication > 5%
