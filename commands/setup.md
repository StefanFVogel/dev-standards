# Claude Code Project Setup

Complete setup for Claude Code: install quality tools, sync commands, and configure permissions.

## Instructions

### Step 1: Run the automated setup

```bash
python standards/scripts/maintain_tools.py --setup
```

This installs:
- **Python:** Ruff, Vulture, SQLFluff, Pyright, Radon, djLint
- **Node.js:** Biome, Knip, jscpd (via nodeenv if npm not available)

And synchronizes:
- **Commands:** `standards/commands/*.md` → `.claude/commands/`
- **Permissions:** `standards/docs/claude_permissions.json` → `.claude/settings.local.json`

### Step 2: Verify permissions

1. Read `.claude/settings.local.json`
2. Read `standards/docs/claude_permissions.json`
3. Compare: every permission from the template (with `{{PROJECT_ROOT_UNIX}}` resolved to the actual project root) must be present in `settings.local.json`
4. If any are missing, add them and save the file
5. If any extra `deny` rules exist that are NOT in the template, leave them (user customization)

### Step 3: Verify commands

1. List files in `.claude/commands/`
2. List files in `standards/commands/`
3. Every `.md` file from `standards/commands/` must exist in `.claude/commands/` with identical content
4. If any are missing or outdated, re-run step 1

### Step 4: Report

Print a summary:

| Component        | Status |
|------------------|--------|
| Python Tools     | ...    |
| Node.js Tools    | ...    |
| Commands         | ...    |
| Permissions      | ...    |

If everything is OK, report: "Setup complete — all components configured."
