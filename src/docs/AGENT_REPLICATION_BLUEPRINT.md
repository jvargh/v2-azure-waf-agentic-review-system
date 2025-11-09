# Azure Well-Architected Agent Replication Blueprint

## Quick Start: Build a New Pillar Agent in 30 Minutes

### Prerequisites
- Pillar domain codes defined (e.g., RE01-RE10 for Reliability)
- Sample architecture text for testing
- Scoring criteria identified

---

## Step 1: Define Pillar Constants (5 min)

Create `src/app/agents/<pillar>_constants.py`:

```python
PILLAR_CODE = "reliability"  # lowercase identifier
PILLAR_PREFIX = "RE"         # domain code prefix

DOMAIN_TITLES = {
    "RE01": "Reliability-Focused Design Foundations",
    "RE02": "Identify and Rate User and System Flows",
    "RE03": "Perform Failure Mode Analysis (FMA)",
    "RE04": "Define Reliability and Recovery Targets",
    "RE05": "Add Redundancy at Different Levels",
    "RE06": "Implement a Timely and Reliable Scaling Strategy",
    "RE07": "Strengthen Resiliency with Self-Preservation and Self-Healing",
    "RE08": "Test for Resiliency and Availability Scenarios",
    "RE09": "Implement Structured, Tested, and Documented BCDR Plans",
    "RE10": "Measure and Model the Solution's Health Indicators",
}
```

---

## Step 2: Create Agent Instructions (10 min)

File: `src/app/prompts/<pillar>_agent_instructions.txt`

**Template:**
```
You are an Azure Well-Architected Framework <PILLAR> expert.
Evaluate the architecture strictly against <CODE_PREFIX>01–<CODE_PREFIX>10 checklist items.

Output ONLY valid JSON matching this schema:
{
  "overall_score": int (0-100),
  "domain_scores": {
    "<CODE_PREFIX>01": {"score": int, "title": string},
    "<CODE_PREFIX>02": {"score": int, "title": string},
    ...
    "<CODE_PREFIX>10": {"score": int, "title": string}
  },
  "recommendations": [
    {
      "title": string,
      "description": string,
      "priority": int (1=critical, 2=high, 3=medium),
      "impact_score": int (1-10),
      "pillar_codes": [string, ...]
    }
  ],
  "mcp_references": [
    {"title": string, "url": string}
  ]
}

Provide only the JSON object. No preamble or explanation.
```

**Replace:**
- `<PILLAR>` → pillar name
- `<CODE_PREFIX>` → your prefix (RE, SE, PE, etc.)
- Add domain-specific evaluation criteria

---

## Step 3: Create Scoring Definition (10 min)

File: `src/utils/scoring/<pillar>_pillar.json`

**Structure:**
```json
{
  "pillar": "reliability",
  "practices": [
    {
      "code": "RE01",
      "title": "Reliability-Focused Design Foundations",
      "weight": 0.08,
      "signals": [
        "availability zone",
        "redundancy",
        "multi-region",
        "failover"
      ],
      "category": "Design"
    },
    {
      "code": "RE02",
      "title": "...",
      "weight": 0.10,
      "signals": ["critical flow", "user journey"],
      "category": "Requirements"
    }
  ]
}
```

**Requirements:**
- 10 practices minimum
- Weights sum to ~1.0
- Signals: keywords to match in architecture text (lowercase)
- Categories: group practices for breakdown reporting

---

## Step 4: Copy Agent Implementation (5 min)

Copy `reliability_agent.py` → `<pillar>_agent.py`

**Find/Replace:**
1. `ReliabilityAssessment` → `<Pillar>Assessment`
2. `ReliabilityAgent` → `<Pillar>Agent`
3. `RE_TITLES` → `DOMAIN_TITLES` (import from constants)
4. `"reliability"` → `"<pillar>"`
5. `reliability_agent_instructions.txt` → `<pillar>_agent_instructions.txt`
6. `reliability_pillar.json` → `<pillar>_pillar.json`

**Critical Updates:**
- Line ~14: `from src.app.agents.<pillar>_constants import DOMAIN_TITLES, PILLAR_CODE`
- Line ~155: Use `DOMAIN_TITLES` instead of hard-coded dict
- Line ~345: `pillar="<pillar>"`
- Line ~547: Update argparse description

---

## Step 5: Create Sample Architecture Fixture

File: `tests/fixtures/<pillar>_sample_architecture.txt`

**Guidelines:**
- 300-500 words
- Include architecture patterns relevant to pillar
- Mix good and bad practices
- Trigger at least 5 domain codes
- Include specific technology names (Azure services, patterns)

**Example snippet:**
```
Sample Azure AI Application Architecture:

Core Infrastructure:
- Azure OpenAI (East US, no redundancy)
- App Service (Basic B1, single instance)
- No availability zones configured

[Add details specific to your pillar focus areas]
```

---

## Step 6: Schema Contract (Reference)

### Assessment Object
```python
{
  "overall_score": int,           # 0-100
  "domain_scores": {
    "CODE": {
      "score": int,                # 0-100
      "title": str
    }
  },
  "recommendations": [
    {
      "title": str,
      "description": str,
      "priority": int,             # 1-3
      "impact_score": int,         # 1-10
      "pillar_codes": [str],       # e.g., ["RE01","RE05"]
      "severity": int              # derived: 1-5
    }
  ],
  "mcp_references": [
    {"title": str, "url": str}
  ],
  "maturity": {
    "overall_maturity_percent": float,
    "pillar": str,
    "practice_scores": [...],
    "gaps": [...],
    "recommendations": [...]
  },
  "timestamp": str
}
```

### Severity Derivation
```python
if rec.get("severity"): use it
elif rec.get("priority"): use it
elif impact_score >= 9: severity = 1
elif impact_score >= 7: severity = 2
elif impact_score >= 5: severity = 3
elif impact_score >= 3: severity = 4
else: severity = 5
```

**Keep ALL original fields** (priority, impact_score, pillar_codes) + add severity.

---

## Step 7: Test (Quick Validation)

Run:
```powershell
python azure-well-architected-agents\src\app\agents\<pillar>_agent.py
```

**Expected outputs:**
- Console: LLM score, recommendation count, maturity %
- `src/results/RESULTS.md` created
- JSON includes all 10 domain codes
- Recommendations have priority, impact_score, pillar_codes, severity

**Validation checklist:**
- [ ] All domain codes present with titles
- [ ] Recommendations >= 3
- [ ] No parse errors
- [ ] Markdown sections complete
- [ ] Maturity % calculated

---

## Step 8: Write Tests

File: `tests/test_<pillar>_agent_e2e.py`

**Copy from** `test_reliability_agent_e2e.py` and adjust:
1. Import `<Pillar>Agent`
2. Update fixture path
3. Check domain codes match your prefix
4. Validate recommendation schema

**Minimal test:**
```python
@pytest.mark.asyncio
async def test_pillar_agent_schema():
    agent = SecurityAgent(enable_mcp=False)
    arch = Path("tests/fixtures/security_sample_architecture.txt").read_text()
    assessment = await agent.assess_architecture(arch)
    
    # All domain codes present
    assert len(assessment.domain_scores) == 10
    for code in ["SE01", "SE02", ...]:
        assert code in assessment.domain_scores
        assert "title" in assessment.domain_scores[code]
        assert "score" in assessment.domain_scores[code]
    
    # Recommendations preserve schema
    for rec in assessment.recommendations:
        assert "priority" in rec
        assert "impact_score" in rec
        assert "pillar_codes" in rec
        assert "severity" in rec
```

---

## Step 9: CLI Usage

### Basic run:
```powershell
python azure-well-architected-agents\src\app\agents\<pillar>_agent.py
```

### Quiet mode (truncated JSON):
```powershell
python azure-well-architected-agents\src\app\agents\<pillar>_agent.py --quiet
```

### Full JSON even in quiet:
```powershell
python azure-well-architected-agents\src\app\agents\<pillar>_agent.py --quiet --json
```

---

## Step 10: Update Project README

Add section:
```markdown
### Security Agent
Evaluates architecture against Security pillar best practices (SE01-SE10).

**Run:**
```powershell
python azure-well-architected-agents\src\app\agents\security_agent.py
```

**Output:** `src/results/RESULTS.md` + console summary
```

---

## Common Patterns (Reference)

### Domain Code Naming
- **RE**: Reliability (RE01-RE10)
- **SE**: Security (SE01-SE10)
- **PE**: Performance Efficiency (PE01-PE10)
- **CO**: Cost Optimization (CO01-CO10)
- **OP**: Operational Excellence (OP01-OP10)
- **SU**: Sustainability (SU01-SU10)

### Weight Distribution Strategy
- Critical practices: 0.12-0.15
- Important practices: 0.08-0.10
- Supporting practices: 0.05-0.07
- Total: ~1.0

### Signal Selection
- Use lowercase keywords
- Include synonyms/variants
- Mix technology names + patterns
- Test against sample architecture

### Recommendation Priority Guidance
- **1 (Critical)**: Security vulnerabilities, single points of failure, data loss risks
- **2 (High)**: Performance bottlenecks, cost inefficiencies, compliance gaps
- **3 (Medium)**: Best practice improvements, optimization opportunities

---

## Troubleshooting

### Issue: Domain scores missing titles
**Fix:** Ensure `DOMAIN_TITLES` imported and used in `_parse_response`

### Issue: Recommendations missing fields
**Fix:** Check `_normalize_recommendations` doesn't drop priority/impact_score

### Issue: Parse errors
**Fix:** Validate instructions file asks for exact JSON schema

### Issue: Low maturity scores
**Fix:** Add more signals to scoring JSON; verify signal matching logic

### Issue: No MCP references
**Fix:** Check MCP manager initialization; may require live service

---

## Files Modified Per New Pillar

**Created (5 files):**
1. `src/app/agents/<pillar>_constants.py`
2. `src/app/agents/<pillar>_agent.py`
3. `src/app/prompts/<pillar>_agent_instructions.txt`
4. `src/utils/scoring/<pillar>_pillar.json`
5. `tests/fixtures/<pillar>_sample_architecture.txt`

**Updated (2 files):**
6. `tests/test_<pillar>_agent_e2e.py` (copy + adjust)
7. `README.md` (add pillar section)

**Total time:** ~30 min per pillar (after first one)

---

## Quality Gates

Before considering pillar complete:
- [ ] All 10 domain codes return scores
- [ ] Recommendations include all 5 required fields
- [ ] Tests pass
- [ ] Manual run produces valid markdown
- [ ] JSON schema validated
- [ ] No cognitive complexity warnings >15
- [ ] Documentation updated

---

## Next Steps After All Pillars Built

1. **Extract base class** (`PillarAgent`) to eliminate duplication
2. **Unified CLI runner** accepting `--pillar` flag
3. **Schema validator** as pre-output check
4. **JSON artifact** output (RESULTS.json)
5. **Caching layer** for deterministic scores
6. **Observability hooks** (optional re-enable)
7. **Multi-pillar reports** (combined assessment)

---

## Reference: Current Reliability Agent Features

**Implemented:**
- ✅ Nested domain_scores objects (score + title)
- ✅ Canonical domain title map
- ✅ Quiet mode (truncated JSON)
- ✅ Full JSON mode (complete output)
- ✅ `--quite` alias support
- ✅ Deterministic maturity scoring
- ✅ Gap analysis integration
- ✅ Markdown report generation
- ✅ Telemetry disabled
- ✅ Environment auto-discovery

**Pending:**
- ⏳ Recommendation schema full preservation (priority, impact_score, pillar_codes)
- ⏳ JSON artifact file (RESULTS.json)
- ⏳ Schema validation helper
- ⏳ Complexity refactoring
- ⏳ Test updates for new schema

**Optional:**
- 💡 Raw LLM JSON dump flag
- 💡 Output directory customization
- 💡 Caching layer
- 💡 Base class extraction

---

## Support

For questions or issues during replication:
1. Check this blueprint section-by-section
2. Compare against working `reliability_agent.py`
3. Validate JSON schema contract
4. Review test expectations
5. Check environment variables loaded

**Common mistake:** Forgetting to update imports after file copy/rename.
**Quick fix:** Search for "reliability" string in new agent file and replace with pillar name.
