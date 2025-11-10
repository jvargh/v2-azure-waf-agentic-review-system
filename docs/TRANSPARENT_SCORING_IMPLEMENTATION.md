# Transparent Scoring Implementation - Complete

## Changes Implemented

### 1. Backend Changes (`backend/server.py`)

#### New Models Added:
- **`SubcategoryDetail`**: Tracks transparent breakdown of subcategory scoring
  - `base_score`: Raw LLM assessment before penalties
  - `coverage_penalty`: Points deducted for missing concepts
  - `gap_penalty`: Points deducted for negative mentions
  - `final_score`: After all adjustments
  - `confidence`: High/Medium/Low
  - `evidence_found`: Key concepts detected
  - `missing_concepts`: Expected but not found
  - `gaps_detected`: Specific issues mentioned
  - `human_summary`: Plain-English one line summary of coverage quality
  - `expected_concepts`: Full list of concepts evaluated for this subcategory
  - `substantiated`: Boolean indicating whether any evidence concepts were found

#### Enhanced Models:
- **`Recommendation`**: Added `points_recoverable` field to show potential improvement
- **`PillarResult`**: Added new fields:
  - `subcategory_details`: Per-subcategory breakdown with penalties
  - `gap_based_recommendations`: Recommendations generated from penalty analysis
  - `normalization_applied`: Flag if subcategories summed > 100
  - `raw_subcategory_sum`: Sum before normalization
    - `expected_concepts`: Scoped list of concepts evaluated for this subcategory (only concepts actually assigned to and evaluated for this subcategory: concatenation of `evidence_found + missing_concepts` with de-duplication)
#### Scoring Logic Changes (`evaluate_pillar` function):
**OLD APPROACH** (Top-Down):
1. Calculate evidence_score from conservative scoring
2. Scale LLM subcategories to match evidence_score
3. Apply elevation logic (can increase pillar score)
4. Force subcategories to sum to final pillar score
❌ **Problem**: Pillar score and subcategory sum could mismatch

**NEW APPROACH** (Bottom-Up):
1. LLM assesses each subcategory based on documentation quality
2. Subcategories scored individually with evidence-based penalties
3. **Pillar score = sum of all subcategories** (natural aggregate)
4. Only normalize if sum > 100 (scale down to fit 0-100 range)
5. Generate gap-based recommendations from normalization penalties
✅ **Result**: Pillar score always matches subcategory sum

#### Gap-Based Recommendation Generation:
When `normalization_applied = true`:
- Calculate penalty points: `raw_subcategory_sum - 100`
- Generate high-priority recommendation explaining the gaps
- Provide actionable guidance on which subcategories to improve
- Show `points_recoverable` to quantify improvement potential

### 2. Frontend Changes

#### Types Updated (`frontend/src/types.ts`):
- Added `points_recoverable?: number` to `Recommendation`
- Added to `PillarScore`:
  - `gapBasedRecommendations?: Recommendation[]`
  - `normalizationApplied?: boolean`
  - `rawSubcategorySum?: number`

#### UI Enhancements (`frontend/src/components/ResultsScorecardTab.tsx`):
- **New Section**: "Hidden Gap Analysis" (displayed between pillar boxes and "How Scores Work")
  - Shows warning when normalization was applied
  - Displays pillar name with before/after normalization values
  - Lists gap-based recommendations with:
    - Title explaining the gap
    - Reasoning (why gaps exist)
    - Recommendation (how to fix)
    - Points recoverable (quantified improvement)
  - Yellow warning styling to draw attention

## How It Works Now

### Example: Reliability Pillar

**Before (Hidden Penalties)**:
- Subcategories display: 14+9+10+10+10+... = **141 points**
- Pillar score shows: **100**
- User confusion: "Why doesn't 141 = 100?"
- No visibility into what was penalized

**After (Transparent)**:
- Subcategories display: 14+9+10+10+10+... = **141 points**
- Pillar score shows: **100** (normalized)
- ⚠️ Hidden Gap Analysis section appears:
  - "Reliability (Normalized from 141 → 100)"
  - Recommendation: "Address 41 Points of Hidden Gaps to Achieve True Maturity"
  - Explanation: Subcategories sum to 141, indicating 41 points of gaps
  - Actionable advice: Focus on subcategories scoring below 8 points
  - Quantified: "Potential improvement: +41 points"

### Score Calculation Flow:

```
LLM Assessment
↓
Subcategory Scores: [14, 9, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
↓
Sum = 141 points
↓
Check: 141 > 100? YES
↓
Normalization Applied:
- scale_factor = 100 / 141 = 0.709
- Each subcategory × 0.709
- Final subcategories: [10, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7] = 100
↓
Pillar Score = 100
↓
Generate Gap Recommendation:
- Title: "Address 41 Points of Hidden Gaps..."
- Points Recoverable: 41
- Priority: High
```

## Benefits

### 1. **Transparency**
- Users see exactly how scores were calculated
- No more "black box" scoring
- Clear understanding of penalties applied

### 2. **Actionability**
- Specific recommendations tied to penalties
- Quantified improvement potential
- Clear priority areas for remediation

### 3. **Mathematical Consistency**
- Pillar score ALWAYS = sum of subcategories
- No more mismatches (84 vs 79)
- Bottom-up aggregation is intuitive

### 4. **Better User Experience**
- Warning section draws attention to gaps
- Color-coded (yellow) for visibility
  - Explicit foundational guidance for zero-evidence areas
- Expandable details for each pillar
- Shows before/after normalization values

## Testing

✅ Backend compiles successfully
✅ Frontend builds without errors
✅ New fields are optional (backward compatible)
✅ Existing assessments will work (fields will be undefined/null)

## Rollback Instructions

The legacy backup folder (`backup_transparent_scoring_YYYYMMDD_*`) has been removed to reduce repo size and duplication. Use Git history for rollback instead of .bak files.

```powershell
# Example: restore previous version of backend/server.py and frontend components
git log --oneline -- backend/server.py frontend/src/components/ResultsScorecardTab.tsx frontend/src/types.ts

# Checkout a prior commit (replace <commit> with the desired hash)
git checkout <commit> -- backend/server.py frontend/src/components/ResultsScorecardTab.tsx frontend/src/types.ts

Write-Host "✓ Rollback via git history complete"
```

If you need a point-in-time snapshot before major scoring changes, create a lightweight tag first:

```powershell
git tag -a pre-transparent-scoring -m "State before transparent scoring implementation"
git push origin pre-transparent-scoring
```

## Next Steps

1. **Start backend and frontend servers**:
   ```powershell
   # Terminal 1 - Backend
   cd backend
   $env:PYTHONPATH='C:\_Projects\MAF\wara\azure-well-architected-agents'
   python -m uvicorn server:app --host 127.0.0.1 --port 8000

   # Terminal 2 - Frontend  
   cd frontend
   npm run dev
   ```

2. **Run a new assessment** to see the transparent scoring in action

3. **Verify**:
   - Pillar scores match subcategory sums
   - Gap-based recommendations appear when normalization applied
   - Warning section is visible and actionable

## Impact on Existing Assessments

**IMPORTANT**: The transparent scoring changes do NOT automatically apply to existing completed assessments.

Assessments are stored in MongoDB with their original scores and will continue to display those scores until explicitly rescored.

### How to Apply Transparent Scoring to Existing Assessments

The system includes a **rescore endpoint** that allows you to update existing assessments without re-uploading documents:

#### Rescore Single Assessment
```bash
# Via API
curl -X POST http://localhost:8000/api/assessments/{assessment_id}/rescore

# Via Python script
python scripts/rescore_existing_assessments.py assess_1234567890
```

#### Rescore All Assessments
```bash
# Via API
curl -X POST http://localhost:8000/api/assessments/rescore-all

# Via Python script
python scripts/rescore_existing_assessments.py --all
```

#### List Available Assessments
```bash
python scripts/rescore_existing_assessments.py --list
```

### What Happens During Rescore

1. Retrieves original documents/corpus from storage
2. Preserves LLM-generated subcategory structure
3. Applies new bottom-up scoring logic
4. Generates gap-based recommendations if normalization occurs
5. Updates assessment with new fields (normalization_applied, raw_subcategory_sum, gap_based_recommendations)
6. Preserves old scores in score_history for rollback

### Forward Compatibility

**New Assessments**: Automatically use transparent scoring

**Old Assessments**: 
- Display normally without gap analysis section (fields are optional)
- Can be rescored anytime to apply transparent scoring
- Original scores preserved in score_history before updating

**See `docs/RESCORING_GUIDE.md` for complete documentation.**

## Code Locations

- Backend model changes: Lines 102-155
- Backend scoring logic: Lines 1868-1920  
- Frontend type changes: Lines 14-54
- Frontend UI changes: Lines 209-265
