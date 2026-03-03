# Automated Review-Fix Loop

Run the project's automated code quality review and fix all findings iteratively.

## Instructions

Execute this loop up to **3 iterations** (stop early if GREEN):

### Iteration N (N = 1, 2, 3):

1. **Run the review:**
   ```bash
   PYTHONIOENCODING=utf-8 python standards/scripts/maintain_tools.py --mode branch
   ```

2. **Parse the output** and check the Architekten-Ampel:
   - If **GREEN**: Stop. Report "Ampel GREEN — keine Findings." to the user.
   - If **YELLOW or RED**: Continue to step 3.

3. **Categorize findings** from the output:
   - **Complexity (Radon)**: Functions with CC rank C or worse → refactor (extract helpers, early returns)
   - **Dead Code (Vulture)**: Unused imports/functions/variables → remove them
   - **Duplicates (jscpd)**: Duplicated blocks → extract shared helpers or constants
   - **Linting (Ruff/Biome)**: Style violations → fix according to the linter's suggestion
   - **HTML (djLint)**: Template issues → fix indentation/structure

4. **Fix ONLY findings in files changed on this branch** (not pre-existing issues in other files).
   - For each finding, read the affected file, apply the fix, verify it doesn't break logic.
   - Do NOT introduce new features or refactor beyond what the finding requires.

5. **Go to next iteration** (back to step 1).

### After 3 iterations (or GREEN reached):

Report a summary table to the user:

| Iteration | Ampel | Findings Fixed |
|-----------|-------|----------------|
| 1         | ...   | ...            |
| 2         | ...   | ...            |
| 3         | ...   | ...            |

If still not GREEN after 3 iterations, list the **remaining findings** that could not be resolved and explain why (e.g., pre-existing complexity in allowlisted files, vendor library duplicates).
