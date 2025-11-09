# Conservative Evidence-Based Scoring Implementation

## Overview
Implemented a conservative, evidence-based scoring system that rewards comprehensive architectural documentation and penalizes sparse evidence. This replaces the previous generous heuristic that could score 70-85 even on minimal documentation.

## Changes Implemented

### 1. Backend: Conservative Scoring Function
**File:** `backend/server.py`

#### New Function: `_calculate_conservative_score()`
Located before `_evaluate_pillar()`, this function implements:

- **Concept Coverage Analysis**: Defines pillar-specific concepts in three tiers:
  - **Critical** (50% weight): Core concepts essential to the pillar (e.g., "redundancy", "failover" for reliability)
  - **Important** (30% weight): Supporting concepts that demonstrate maturity
  - **Nice-to-have** (20% weight): Advanced practices

- **Corpus Density Adjustment**: 
  - Minimal (<500 chars): 40% multiplier
  - Moderate (500-2000 chars): 70% multiplier
  - Comprehensive (>2000 chars): 100% multiplier

- **Absence Penalties**:
  - Missing >50% of critical concepts: 30% score reduction
  - Ensures low scores when fundamental concepts are absent

- **Confidence Calculation**:
  - **Low**: <30% concept coverage OR <500 chars
  - **Medium**: 30-70% coverage OR 500-2000 chars
  - **High**: >70% coverage AND >2000 chars

#### Scoring Formula:
```
raw_score = (critical_found / critical_total * 50) 
          + (important_found / important_total * 30) 
          + (nice_found / nice_total * 20)

adjusted_score = raw_score * density_multiplier

if critical_coverage < 50%:
    adjusted_score = adjusted_score * 0.7

overall_score = clamp(adjusted_score, 0, 100)
```

### 2. Backend: Updated PillarResult Model
**File:** `backend/server.py`

Added `confidence` field to `PillarResult`:
```python
class PillarResult(BaseModel):
    pillar: str
    overall_score: int
    subcategories: Dict[str, int]
    recommendations: List[Recommendation]
    confidence: str = "Low"  # Low|Medium|High
```

### 3. Backend: Fallback Logic Update
**File:** `backend/server.py` - `_evaluate_pillar()` function

Replaced generous heuristic with conservative scoring:
```python
# OLD (removed):
hits = sum(corpus.lower().count(k) for k in keywords.get(code, [])) + 1
base_score = min(90, 55 + hits * 3)  # Could reach 70-85 easily

# NEW:
overall_score, confidence, subcats = _calculate_conservative_score(corpus, code, name)
return PillarResult(..., confidence=confidence)
```

Real agent paths now also return `confidence="High"` since they have framework-backed analysis.

### 4. Frontend: Type Updates
**File:** `frontend/src/types.ts`

Added confidence to `PillarScore` interface:
```typescript
export interface PillarScore {
  pillar: string;
  score?: number;
  overallScore?: number;
  categories?: { name: string; score: number }[];
  subcategories?: Record<string, number>;
  recommendations?: Recommendation[];
  confidence?: 'Low' | 'Medium' | 'High';  // NEW
}
```

### 5. Frontend: Confidence Badge UI
**File:** `frontend/src/components/ResultsScorecardTab.tsx`

Added confidence badge next to pillar name in scorecard:
```tsx
<h3>
  {pillar.pillar}
  <span 
    title={confidenceTooltip}
    style={{ 
      marginLeft: '.5rem',
      padding: '.15rem .4rem',
      backgroundColor: confidenceColor,  // Green/Yellow/Red
      color: 'white',
      fontSize: '.55rem',
      fontWeight: 600,
      borderRadius: '3px',
      cursor: 'help'
    }}
  >
    {confidence}
  </span>
</h3>
```

**Color coding:**
- High (Green `#28a745`): Comprehensive documentation with >70% concept coverage
- Medium (Yellow `#ffc107`): Moderate documentation with 30-70% concept coverage
- Low (Red `#dc3545`): Minimal documentation with <30% concept coverage

**Tooltips** explain evidence quality on hover.

## Expected Behavior Changes

### Before (Generous Heuristic)
- Minimal architecture doc: **70-75 score**
- Keyword "redundancy" mentioned 3 times: **55 + 3*3 = 64 base score**
- No penalty for missing critical concepts
- No visibility into evidence quality

### After (Conservative Evidence-Based)
- Minimal architecture doc: **10-20 score**, **Low confidence**
  - Few concepts found, small corpus, density penalty applied
- Comprehensive doc with all reliability concepts: **70-85 score**, **High confidence**
  - All critical + important concepts present, large corpus, no penalties
- Moderate doc with some concepts: **35-50 score**, **Medium confidence**
  - Partial concept coverage, moderate corpus size

## Pillar-Specific Concepts

### Reliability
- Critical: redundancy, failover, backup, disaster recovery, availability
- Important: replica, multi-region, health check, monitoring, sla
- Nice-to-have: resiliency, chaos engineering, circuit breaker

### Security
- Critical: encryption, authentication, authorization, key vault
- Important: rbac, network security, firewall, identity, secret
- Nice-to-have: zero trust, threat detection, compliance, audit

### Cost Optimization
- Critical: cost, pricing, budget
- Important: optimization, reserved instance, tagging, monitoring
- Nice-to-have: autoscaling, rightsizing, spot instance

### Operational Excellence
- Critical: monitoring, logging, deployment
- Important: ci/cd, pipeline, automation, alerting
- Nice-to-have: infrastructure as code, gitops, observability

### Performance Efficiency
- Critical: latency, throughput, scalability
- Important: cache, cdn, load balancing, indexing
- Nice-to-have: compression, optimization, query tuning

## Testing Recommendations

### Test Case 1: Minimal Evidence
**Input:** "We use Azure VMs for hosting."
**Expected:**
- All pillars: 0-15 score, Low confidence
- Subcategories reflect minimal evidence across Design/Implementation/Operations

### Test Case 2: Moderate Evidence
**Input:** Multi-paragraph description with 5-10 pillar concepts, 500-1000 chars
**Expected:**
- Relevant pillars: 30-50 score, Medium confidence
- Irrelevant pillars: 10-25 score, Low confidence

### Test Case 3: Comprehensive Evidence
**Input:** Detailed architecture doc with 15+ concepts per pillar, >2000 chars
**Expected:**
- All pillars: 60-85 score, High confidence
- Subcategories show healthy variance

### Test Case 4: Pillar-Specific Gaps
**Input:** Strong security description, weak reliability
**Expected:**
- Security: 60-75 score, High confidence
- Reliability: 15-30 score, Low confidence
- Demonstrates differential scoring based on actual evidence

## Benefits

1. **Transparency**: Users see confidence level and understand assessment quality
2. **Guidance**: Low confidence signals users to add more architectural detail
3. **Accuracy**: Scores reflect actual documentation depth, not keyword density
4. **Alignment**: Scoring methodology aligns with Well-Architected Framework principles of evidence-based assessment
5. **Actionability**: Clear path to improve scores: add comprehensive documentation covering critical concepts

## Migration Path

- Existing assessments retain old scores (backward compatible)
- New assessments use conservative scoring
- Frontend handles both legacy `pillarScores` and new `pillarResults` format
- Confidence defaults to "Low" if missing (safe fallback)

## Files Modified

1. `backend/server.py` - Added conservative scoring function, updated PillarResult model, updated fallback logic
2. `frontend/src/types.ts` - Added confidence field to PillarScore
3. `frontend/src/components/ResultsScorecardTab.tsx` - Added confidence badge with tooltips
4. `test_conservative_scoring.py` - Created comprehensive test suite (new file)
5. `test_scoring_quick.py` - Created quick validation script (new file)
6. `CONSERVATIVE_SCORING.md` - This documentation (new file)
