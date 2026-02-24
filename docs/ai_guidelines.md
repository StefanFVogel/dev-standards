# AI Coding Guidelines & Standards

This document defines the global coding standards and AI behavior rules for all projects.

## 🛡️ Quality Gates & Workflow
Before marking a task as done, you MUST ensure:
1. **No Dead Code:** Run `vulture` or the maintain script.
2. **Low Complexity:** Functions must be simple (Radon CC < 10).
3. **No Duplication:** DRY principle is strictly enforced.

## 🐍 Python Standards
- **Typing:** All function signatures must have type hints.
- **Docstrings:** Google Style Guide required for all public modules/classes.
- **Async:** Use `async/await` for I/O bound tasks (DB, API).
- **Error Handling:** No bare `except:`. Use specific exceptions.

## 🏗️ Architecture Patterns
- **API Layer:** No business logic in routers. Use Dependency Injection.
- **Repositories:** All DB access goes here.
- **LLM Tools:** Must inherit from `FunctionTool` and have precise docstrings.

## 🤖 AI Behavior
- **Refactoring:** When refactoring, always prioritize readability and maintainability over cleverness.
- **Tool Usage:** Prefer specialized tools (like `replace_text`) over rewriting entire files to preserve context.
- **Context:** Always check `architect_workflow.md` and `implementation.md` for specific rules before generating code.