# Rescoring Existing Assessments with Transparent Scoring

## Overview

The transparent scoring implementation (November 7, 2025) introduced a bottom-up scoring approach where pillar scores are calculated as the sum of subcategory scores, with normalization only applied when the sum exceeds 100.

**This change does NOT automatically apply to existing completed assessments.** Assessments are stored with their original scores in MongoDB and will continue to display those scores until rescored.

## Why Rescore?

Existing assessments were calculated using the old top-down scoring approach:
- Evidence-based score → Scale subcategories to match → Apply elevation logic
- Scores could be non-deterministic and penalties were hidden

New transparent scoring approach:
- Subcategories assessed by LLM → Sum = Pillar score → Only normalize if >100
- Generates gap-based recommendations showing points recoverable
- Full transparency through "Hidden Gap Analysis" UI

## How to Rescore

### Option 1: Rescore a Single Assessment

**Via API:**
```bash
curl -X POST http://localhost:8000/api/assessments/{assessment_id}/rescore
```

**Via Python script:**
```bash
python scripts/rescore_existing_assessments.py assess_1234567890
```

### Option 2: Rescore All Assessments

**Via API:**
```bash
curl -X POST http://localhost:8000/api/assessments/rescore-all
```

**Via Python script:**
```bash
python scripts/rescore_existing_assessments.py --all
```

### Option 3: List Available Assessments

To see which assessments are available to rescore:

```bash
python scripts/rescore_existing_assessments.py --list
```

## What Happens During Rescore

1. **Retrieves Original Data**: Fetches the stored assessment and rebuilds the unified corpus from documents
2. **Preserves Subcategory Structure**: Keeps the original LLM-generated subcategory names and structure
3. **Applies Bottom-Up Scoring**: 
   - Computes pillar score as sum of subcategory scores
   - Only normalizes if sum > 100
   - Generates gap recommendations when normalization occurs
4. **Updates Metadata**:
   - Adds `gap_based_recommendations` with points recoverable
   - Sets `normalization_applied` flag
   - Records `raw_subcategory_sum` before normalization
5. **Preserves Recommendations**: Keeps all original recommendations and adds gap-based ones
6. **Updates Score History**: Snapshots old scores before updating

## Expected Changes After Rescore

### Before (Old Scoring):
```json
{
  "pillar": "Reliability",
  "overall_score": 100,
  "subcategories": {
    "Backup Strategy": 22,
    "Disaster Recovery": 24,
    "High Availability": 31,
    "Monitoring": 27,
    "Testing": 27
  },
  "normalization_applied": null,
  "raw_subcategory_sum": null,
  "gap_based_recommendations": []
}
```
**Subcategories sum to 131**, but score shows as 100. No explanation of the hidden 31-point gap.

### After (Transparent Scoring):
```json
{
  "pillar": "Reliability",
  "overall_score": 100,
  "subcategories": {
    "Backup Strategy": 22,
    "Disaster Recovery": 24,
    "High Availability": 31,
    "Monitoring": 27,
    "Testing": 27
  },
  "normalization_applied": true,
  "raw_subcategory_sum": 131,
  "gap_based_recommendations": [
    {
      "title": "Address 31 Points of Hidden Gaps to Achieve True Maturity",
      "priority": "High",
      "points_recoverable": 31,
      "reasoning": "Your Reliability subcategories sum to 131 points, but were normalized to 100. This indicates 31 points worth of gaps..."
    }
  ]
}
```
**Transparent**: Shows raw sum was 131, normalized to 100, and provides actionable recommendation to recover 31 points.

## UI Impact

After rescoring, assessments will display the **"Hidden Gap Analysis"** section (yellow warning box) when pillars have normalization applied:

```
⚠️ Score Normalization Applied

Some pillar scores were normalized to fit the 0-100 scale. The gaps below represent areas 
where your architecture could improve beyond the normalized score.

Reliability
  Normalized from 131 → 100

Recommendations to recover 31 points:
  • Address 31 Points of Hidden Gaps to Achieve True Maturity (High priority)
    Addressing these gaps can improve your true Reliability maturity by up to 31 points
```

## Rollback

If you need to rollback to old scores, the original scores are preserved in the `score_history` field:

```json
{
  "score_history": [
    {
      "timestamp": "2025-11-07T10:30:00Z",
      "overall_architecture_score": 84.2,
      "pillar_scores": {
        "Reliability": 100,
        "Security": 94,
        ...
      },
      "score_source": {
        "Reliability": "elevated",
        ...
      }
    }
  ]
}
```

## Important Notes

1. **Requires Original Documents**: Assessment must have documents or unified_corpus to rescore
2. **Preserves Recommendations**: All original recommendations are kept, gap recommendations are added
3. **Updates Overall Score**: The overall architecture score is recalculated as average of new pillar scores
4. **Non-Destructive**: Original scores are preserved in score_history before updating
5. **Backward Compatible**: Old assessments without new fields will still display correctly (optional fields)

## Troubleshooting

**"assessment not found"**
- Check that the assessment ID is correct
- Use `--list` to see available assessments

**"no documents or corpus available to rescore"**
- Assessment was created without uploading documents
- Cannot rescore assessments without original architecture data

**"Cannot connect to API server"**
- Make sure backend server is running on port 8000
- Check: `http://localhost:8000/health`

**Scores didn't change much**
- If subcategory sum was already close to 100, rescoring won't show major changes
- The main benefit is transparency (normalization_applied flag and gap recommendations)

## Migration Strategy

For production deployments with many existing assessments:

1. **Test on Single Assessment**: Rescore one assessment and verify results
2. **Batch Rescore**: Use `rescore-all` endpoint during maintenance window
3. **Monitor**: Check logs for any failures during bulk rescore
4. **Communicate**: Inform users that scores may change slightly due to new methodology
5. **Rollback Plan**: Keep backups of MongoDB before bulk rescore

## API Reference

### POST /api/assessments/{aid}/rescore

Rescore a single assessment.

**Response**: Updated Assessment object with new scores and transparent fields

**Status Codes**:
- 200: Success
- 404: Assessment not found
- 400: Cannot rescore (no documents)
- 500: Rescoring failed

### POST /api/assessments/rescore-all

Rescore all assessments in the system.

**Response**: Array of updated Assessment objects

**Status Codes**:
- 200: Success (includes count of rescored assessments)
- 500: Database query or rescoring failed
