# ⚠️ DEPRECATED: src/ Directory

**Status:** This directory has been migrated to `backend/`

**Migration Date:** November 5, 2025

## What Changed

The entire `src/` directory structure has been migrated to `backend/` to support the full-stack architecture with React frontend and FastAPI backend.

### New Module Paths

| Old Path | New Path |
|----------|----------|
| `src.app.agents.*` | `backend.app.agents.*` |
| `src.app.tools.*` | `backend.app.tools.*` |
| `src.app.utils.*` | `backend.app.utils.*` |
| `src.utils.scoring.*` | `backend.utils.scoring.*` |
| `src.utils.env_utils` | `backend.utils.env_utils` |

### What Still Uses src/

The following directory is **still actively used** and has NOT been migrated:
- **`src/app/prompts/`** - Agent instruction files are loaded from this location

This is intentional to avoid breaking the prompt loading logic in `BasePillarAgent`. The prompts directory may be migrated in a future update.

## Migration Guide

### For CLI Commands

**Old:**
```bash
python -m src.app.agents.reliability_agent my_arch.txt
python -m src.app.agents.security_agent my_arch.txt
```

**New:**
```bash
# Set PYTHONPATH first
$env:PYTHONPATH="C:\_Projects\MAF\wara\azure-well-architected-agents"

# Then run commands
python -m backend.app.agents.reliability_agent my_arch.txt
python -m backend.app.agents.security_agent my_arch.txt
```

### For Python Code

**Old:**
```python
from src.app.agents.reliability_agent import ReliabilityAgent
from src.app.agents.security_agent import SecurityAgent
from src.app.agents.cost_agent import CostAgent
```

**New:**
```python
from backend.app.agents.reliability_agent import ReliabilityAgent
from backend.app.agents.security_agent import SecurityAgent
from backend.app.agents.cost_agent import CostAgent
```

### For Tests

All test files in `tests/` have been updated to use `backend.*` imports. If you're writing new tests, use:

```python
from backend.app.agents.cost_agent import CostAgent
from backend.utils.scoring.scoring import compute_pillar_scores
```

## Migration Status

✅ **Completed:**
- [x] Agent modules migrated to `backend/app/agents/`
- [x] Tools migrated to `backend/app/tools/`
- [x] Utils migrated to `backend/app/utils/` and `backend/utils/`
- [x] Scoring engine migrated to `backend/utils/scoring/`
- [x] Server imports updated to use `backend.*`
- [x] Test files updated to use `backend.*`
- [x] Documentation (README.md, TRACING_DIAGNOSTICS.md) updated
- [x] CLI commands validated with new paths

⏸️ **Pending:**
- [ ] Migrate `src/app/prompts/` to `backend/app/prompts/`
- [ ] Update `BasePillarAgent` to load prompts from new location
- [ ] Remove or archive `src/` directory completely

## Removal Timeline

This `src/` directory is marked as **DEPRECATED** but will remain temporarily to support:
1. The prompts directory (`src/app/prompts/`)
2. Any external tools or scripts that haven't been updated yet

**Recommendation:** Plan to remove this directory in the next major version after migrating the prompts directory.

## Questions?

If you encounter issues with the migration, check:
1. Is `PYTHONPATH` set correctly?
2. Are you using the new `backend.*` import paths?
3. Is the virtual environment activated?

For development setup, see the main [README.md](../README.md).
