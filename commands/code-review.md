# Code Review

Run the project's automated code quality review and report findings (read-only, no fixes).

## Instructions

1. **Run the review:**
   ```bash
   PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode commit
   ```

2. **Parse the output** and check the Architekten-Ampel:
   - If **GREEN**: Report "Ampel GREEN — keine Findings." and stop.
   - If **YELLOW or RED**: Continue to step 3.

3. **Categorize and report findings** in a structured table:

   | Category | File | Location | Finding |
   |----------|------|----------|---------|
   | Complexity (Radon) | ... | line:col | CC=X rank Y |
   | Dead Code (Vulture) | ... | line | unused import/function/variable |
   | Duplicates (jscpd) | ... | lines | N lines duplicated with ... |
   | Linting (Ruff/Biome) | ... | line:col | rule: message |
   | HTML (djLint) | ... | line | rule: message |

4. **Do NOT fix anything.** Only report findings. This is a read-only review.

5. **Summary:** Report the Ampel color and total finding count per category.
