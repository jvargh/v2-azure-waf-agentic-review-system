# Normalization & Subcategory Details Migration Guide

**Date:** November 8, 2025  
**Version:** 1.0

## Overview

Recent enhancements introduced **per-subcategory transparency** to the scoring system, providing detailed breakdowns of how base scores transform into final pillar scores through penalties, normalization, and elevation.

## What Changed

### 1. Normalization Helper Function
- **Location:** `backend/server.py::_normalize_subcategories()`
- **Purpose:** Ensures subcategory scores sum to exactly 100 through proportional scaling
- **Algorithm:**
  ```python
  scale_factor = 100.0 / sum(subcats.values())
  normalized = {k: int(v * scale_factor) for k, v in subcats.items()}
  # Adjust for rounding to ensure exact sum of 100
  ```
- **Applied:** Both initial pillar evaluation (`_evaluate_pillar()`) and rescoring endpoint

### 2. Subcategory Details Structure
Each subcategory now includes:
- `base_score` (int): Original LLM-assigned score before adjustments
- `final_score` (int): Score after penalties and normalization
- `coverage_penalty` (int): Deduction for missing critical concepts
- `gap_penalty` (int): Deduction for gaps/risks detected
- `evidence_found` (List[str]): Up to 6 concepts found in architecture
- `missing_concepts` (List[str]): Up to 6 missing concepts
- `gaps_detected` (List[str]): Risk indicators identified
- `normalization_factor` (float): Scale factor applied during normalization

### 3. Penalty Derivation
- **Location:** `backend/server.py::_derive_penalties()`
- **Method:** Heuristic distribution based on scoring breakdown steps
  - **Coverage penalties:** Weighted by `(100 - subcategory_score)` for subcategories with missing concepts
  - **Gap penalties:** Weighted by `(70 - subcategory_score)` for at-risk subcategories (<70 score)
- **Evidence:** Aggregates `evidence_found` and `missing_concepts` from breakdown tiers, deduplicates, limits to 6 items

### 4. Frontend Enhancements
- **Weight Basis Toggle:** Switch between base-weighted and final-weighted percentages
- **Justification Display:** Shows normalization factor in human-readable format
- **Excel Export:** Includes Base, Final, Δ, Weight% columns per subcategory

## Migration Impact

### Historical Assessments
**Status:** Assessments created before this enhancement **lack subcategory details**.

**Symptoms:**
- Subcategory table shows scores but no Base/Final/Δ columns
- No evidence lists or penalty attributions visible
- Normalization factor not displayed

**Solution:** Run batch rescore script to backfill details.

### New Assessments
**Status:** Automatically include full subcategory details.

**Benefits:**
- Complete transparency: base → penalties → normalization → final
- Evidence-based justification per subcategory
- Penalty attribution shows where scores were adjusted

## Rescoring Process

### Manual Rescore (Single Assessment)
```bash
# Using curl
curl -X POST http://localhost:8000/api/assessments/{assessment_id}/rescore

# From Python
import httpx
response = httpx.post(f"http://localhost:8000/api/assessments/{assessment_id}/rescore")
rescored_data = response.json()
```

### Batch Rescore (All Assessments)
```bash
# Dry-run (preview without changes)
python scripts/batch_rescore.py --dry-run

# Execute rescore
python scripts/batch_rescore.py
```

**Requirements:**
- Backend server running on `localhost:8000`
- Python packages: `httpx`, `rich`
- Install: `pip install httpx rich`

**Output:**
- Progress bar with real-time status
- Summary table showing success/failure per assessment
- Final statistics (total, success, failed counts)

## Backward Compatibility

### API Compatibility
✅ **Fully backward compatible**
- Old assessments render without errors
- Missing `subcategory_details` handled gracefully in frontend
- Base fields (`id`, `assessment_name`, `pillar_scores`) unchanged

### Data Compatibility
✅ **No breaking changes**
- Existing MongoDB documents remain valid
- New fields added as optional extensions
- Rescore endpoint creates missing fields on-demand

### UI Compatibility
✅ **Graceful degradation**
- Subcategory table shows scores even without details
- Justification section hides penalty/evidence blocks if unavailable
- Weight basis toggle disabled if `normalization_factor` missing

## Verification Checklist

After rescoring, verify:

- [ ] **Subcategory Sum:** Each pillar's subcategories sum to 100 (or show normalization applied)
- [ ] **Penalty Attribution:** Coverage/gap penalties displayed per subcategory
- [ ] **Evidence Lists:** Found/missing concepts populated (up to 6 items each)
- [ ] **Normalization Factor:** Scale factor shown when normalization applied
- [ ] **Weight Basis Toggle:** Base vs. final weight percentages match calculations
- [ ] **Excel Export:** Includes Base, Final, Δ, Weight% columns

### Quick Verification (New Assessment)
```bash
# Generate fresh assessment
python scripts/generate_fresh_assessment.py

# Check via API
curl http://localhost:8000/api/assessments | jq '.[0].pillar_scores[0].subcategory_details'

# Expected output: Array of objects with base_score, final_score, coverage_penalty, etc.
```

## Rollback Considerations

If issues arise:

1. **Frontend Rollback:** Revert `types.ts` and `ResultsScorecardTab.tsx` to remove subcategory details rendering
2. **Backend Rollback:** Revert `_normalize_subcategories()` and `_derive_penalties()` functions
3. **Data Preservation:** Rescored data includes original scores; no data loss occurs

**Note:** Rollback does not require database changes (new fields simply ignored by old code).

## Performance Notes

- **Rescore Duration:** ~5-15 seconds per assessment (depends on pillar count and LLM latency)
- **Batch Processing:** Sequential to avoid API rate limits; parallelization possible with `asyncio.gather()` if needed
- **Database Impact:** Minimal; updates `pillar_scores` array in existing documents

## Support

For issues or questions:
1. Check backend logs: `backend/server.py` console output
2. Verify API health: `curl http://localhost:8000/health`
3. Review frontend console: Browser DevTools → Console tab

## Summary

The normalization and subcategory details enhancement provides **full transparency** into scoring transformations. Historical assessments require rescoring to populate new fields, but the system remains fully backward compatible. Use `scripts/batch_rescore.py` to migrate all assessments efficiently.

**Action Items:**
1. ✅ Normalization helper implemented
2. ✅ Penalty derivation integrated
3. ✅ Frontend transparency UI complete
4. ⏳ Run batch rescore for historical data
5. ⏳ Verify new assessment includes details
