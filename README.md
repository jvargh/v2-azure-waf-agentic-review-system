# Azure Well-Architected Agentic Review System - v2

Enterprise-grade multi-pillar Azure architecture assessment with transparent scoring, intelligent document analysis, and comprehensive visualization.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-Cloud-0078d4.svg)](https://azure.microsoft.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev)
[![Transparency](https://img.shields.io/badge/Scoring-Transparent-success.svg)](#scoring-methodology)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Setup](#2-quick-setup)
3. [Architecture](#3-architecture)
4. [Document Upload & Analysis Workflow](#4-document-upload--analysis-workflow)
5. [LLM Analysis Process](#5-llm-analysis-process)
6. [Scoring Methodology](#6-scoring-methodology)
7. [Recommendations Generation](#7-recommendations-generation)
8. [Visualization & UI](#8-visualization--ui)
9. [API Usage](#9-api-usage)
10. [Testing](#10-testing)
11. [Advanced Configuration](#11-advanced-configuration)
12. [Documentation Index](#12-documentation-index)
13. [Contributing](#13-contributing)

## 1. Overview

The **Azure Well-Architected Agents** platform provides automated, intelligent assessment of Azure architectures across five Well-Architected Framework pillars:

- **Reliability** (RE01–RE10) – Resiliency, redundancy, disaster recovery
- **Security** (SE01–SE12) – Zero Trust, IAM, data protection, monitoring
- **Cost Optimization** (CO01–CO14) – FinOps, cost modeling, optimization
- **Operational Excellence** (OE01–OE11) – DevOps, monitoring, incident response
- **Performance Efficiency** (PE01–PE12) – Scalability, latency, throughput

### Key Capabilities

- **Multi-Document Ingestion**: Upload architecture docs, diagrams (SVG/PNG/JPG), support case CSVs, PDFs
- **Intelligent Enrichment**: Automated extraction of diagram elements, support case patterns, risk signals
- **Transparent Scoring**: Bottom-up subcategory summation with normalization disclosure and gap analysis
- **Real-Time Thumbnails**: Visual previews for all uploaded artifacts
- **Comprehensive Visualization**: Interactive charts, collapsible panels, severity-coded badges
- **MongoDB Persistence**: Optional durable storage with in-memory fallback
- **Dual LLM Support**: Azure OpenAI or Azure AI Foundry with graceful degradation

## 2. Quick Setup

```bash
# Clone and install
git clone <repo-url>
cd azure-well-architected-agents
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt

# Configure Azure credentials
cp .env.template .env
# Edit .env with your Azure OpenAI details
```

### Optional: Enable MongoDB Persistence

If you want durable storage (instead of in-memory) for assessments, documents, and score history:

1. Install MongoDB (choose one):
  - Windows (Chocolatey): `choco install mongodb --version=7.0.5 -y`
  - Docker (recommended for local dev):
    ```bash
    docker run -d --name wara-mongo -p 27017:27017 mongo:7.0
    ```
2. Set environment variables in `.env`:
  ```bash
  MONGODB_URI=mongodb://localhost:27017
  MONGODB_DATABASE=wara_assessments
  ```
3. (Optional) Create indexes for performance (see `docs/MONGODB_SETUP.md`).
4. Restart backend; server will auto-detect MongoDB and persist new assessments.

Fallback: If MongoDB is unreachable, the backend logs a warning and continues with in-memory storage (non-durable).

**Minimum environment variables** (`.env`):
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Optional tunables**:
```bash
CASE_SUMMARY_MAX_CASES=25              # Max support case bullets in summaries
NO_EVIDENCE_SUBCATEGORY_FLOOR=2        # Minimum score when no evidence found
USE_CURATED_EXPECTED_CONCEPTS=true     # Use pillar concept catalogs
```

**Start services**:
```bash
# Backend
python -m uvicorn backend.server:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Access UI at `http://localhost:5173` (default Vite port).

## 3. Architecture

```
azure-well-architected-agents/
├── backend/
│   ├── server.py                    # FastAPI API + document ingestion
│   ├── app/
│   │   ├── agents/                  # Pillar agents (reliability, security, cost, ops, perf)
│   │   ├── analysis/                # DocumentAnalyzer, AssessmentOrchestrator
│   │   └── tools/                   # MCP, utility functions
│   └── utils/
│       └── concepts.py              # Expected concept catalogs per pillar
├── frontend/
│   ├── src/
│   │   ├── components/              # React UI (upload, progress, scorecard, viz)
│   │   ├── context/                 # Global state (AssessmentsContext)
│   │   └── api/                     # Backend API client
│   └── vite.config.ts
├── scripts/                         # Batch rescoring, analysis scripts
├── tests/                           # pytest suites (API, scoring, persistence)
├── docs/                            # Deep technical documentation
└── results/                         # Generated JSON + Markdown reports
```

**Data Flow Overview**:
```
[User Uploads Docs] 
    ↓
[Document Enrichment Pipeline]
    ↓ 
[Corpus Assembly] → [5 Pillar Agents] → [Concurrent Evaluation]
    ↓
[Scoring Engine] → [Normalization Check] → [Gap Analysis]
    ↓
[Recommendations Generator]
    ↓
[Persistence Layer (MongoDB/In-Memory)]
    ↓
[Frontend Visualization]
```

## 4. Document Upload & Analysis Workflow

When you upload documents through the frontend or API, the system processes them through an intelligent enrichment pipeline that extracts structured information and generates visual previews.

### Upload Flow

```
[User Selects Files] 
    ↓
[POST /api/assessments/{id}/documents] 
    ↓
[File Validation & Storage]
    ↓
[Enrichment Pipeline] ─┬─→ [Architecture Docs] → Extract raw text + structured report
                       ├─→ [Diagrams] → SVG/PNG/JPG analysis + vision extraction
                       ├─→ [Support Cases CSV] → Theme/risk/pattern extraction
                       └─→ [PDFs] → Text extraction + first page render
    ↓
[Thumbnail Generation] ─→ Base64 data URL (80x80 preview)
    ↓
[Store Document Metadata] → MongoDB or in-memory
    ↓
[Return to Frontend] → Display thumbnails + document list
```

### Document Enrichment Details

Each document type undergoes specialized analysis:

#### 1. Architecture Documents (`.txt`, `.md`, `.docx`)
- **Raw Text Extraction**: Full content captured in `raw_text` field
- **Structured Analysis**: Optional LLM-based analysis produces:
  - Key architectural components identified
  - Technology stack summary
  - Risk patterns detected
  - Compliance indicators
- **Output Fields**: `raw_text`, `analysis_metadata.structured_report`

#### 2. Architecture Diagrams (`.svg`, `.png`, `.jpg`)
- **SVG Text Extraction**: Parse text nodes, labels, annotations (via XML parsing)
- **Vision Analysis**: When Azure OpenAI endpoint configured:
  - Send base64-encoded image to GPT-4 Vision
  - Extract components, connections, data flows
  - Identify Azure services depicted
  - Detect architectural patterns
- **Heuristic Fallback**: If vision unavailable:
  - Extract filename tokens (e.g., `webapp-sql-storage.svg` → "webapp", "sql", "storage")
  - Parse SVG text content (max 12 tokens)
  - Flag as `(heuristic fallback)` in `diagram_summary`
- **Strategy Tracking**: `strategy` field records extraction methods used
- **Output Fields**: `raw_extracted_text`, `diagram_summary`, `strategy`

#### 3. Support Case CSV (`.csv`)
- **Column Detection**: Looks for `title`, `msdfm_productname`, `msdfm_customerstatement`, `msdfm_resolution`, `msdfm_rootcausedescription`
- **Thematic Classification**: Groups cases into categories:
  - Configuration errors
  - Performance issues
  - Security incidents
  - Availability failures
  - Capacity problems
- **Risk Signal Extraction**: Identifies high-severity patterns:
  - Recurring failures
  - Data loss incidents
  - Extended outages
  - Security breaches
- **Sample Arrays**:
  - `root_cause_samples`: First 8 distinct root cause excerpts (>20 chars)
  - `resolution_samples`: First 8 distinct resolution actions
  - `recurring_failure_patterns`: Pattern counts (e.g., `[("configuration_error", 12), ...]`)
- **Truncation**: Summary limited by `CASE_SUMMARY_MAX_CASES` (default 25)
- **Output Fields**: `support_cases_summary`, `total_cases`, `risk_signals`, `thematic_patterns`, `root_cause_samples`, `resolution_samples`, `recurring_failure_patterns`

#### 4. PDF Documents (`.pdf`)
- **Text Extraction**: Full document text via PyMuPDF
- **First Page Thumbnail**: Rasterize page 1 at 150 DPI, resize to 80x80
- **Output Fields**: `raw_text`, `thumbnail_url`

### Thumbnail Generation

All uploaded files receive visual previews:

| File Type | Method | Fallback |
|-----------|--------|----------|
| **SVG** | Parse viewBox, rasterize with Pillow to PNG | Use filename-based icon |
| **PNG/JPG** | Resize with aspect preservation (LANCZOS) | Grayscale placeholder |
| **PDF** | Render first page with PyMuPDF (fitz) | Document icon placeholder |
| **Text/CSV** | Render first 10 lines on white canvas | Text icon placeholder |

Thumbnails encoded as base64 data URLs: `data:image/png;base64,iVBORw0KG...`

### Corpus Assembly

After enrichment, the system builds a **unified corpus** for analysis by prioritizing enriched fields:

**Priority Order**:
1. **Explicit enrichment fields**: `diagram_summary`, `support_cases_summary`, `raw_extracted_text`
2. **Structured reports**: `analysis_metadata.structured_report`
3. **Raw content**: `raw_text`
4. **Legacy field** (deprecated): `llm_analysis` (will be removed in future release)

**Example Corpus Section**:
```markdown
### Architecture Document: webapp-design.md
[raw_text content or structured_report narrative]

### Diagram Analysis: architecture-diagram.svg
Strategy: svg_text_nodes, llm_provider_vision
Components Detected:
- Azure App Service (Web App)
- Azure SQL Database (Primary + Geo-Replica)
- Azure Storage (Blob + Queue)
- Application Gateway (WAF enabled)
...

### Historical Azure Support Cases (Context)
Total Cases: 47

**Risk Signals**:
- 8 incidents involving database failover delays
- 3 data loss events during region outage
- 12 performance degradation cases (query timeout)

**Thematic Patterns**:
- Configuration Errors: 15 cases
- Performance Issues: 18 cases
- Availability Failures: 10 cases
...
```

This unified corpus is then passed to each pillar agent for evaluation.

## 5. LLM Analysis Process

Once the corpus is assembled, the **AssessmentOrchestrator** coordinates parallel evaluation across all five pillars.

### Orchestration Flow

```
[Unified Corpus Ready]
    ↓
[AssessmentOrchestrator.run_assessment(corpus)]
    ↓
┌────────────────────────────────────────────────────────────────┐
│  Launch 5 Concurrent Pillar Agent Tasks (asyncio.gather)      │
├────────────────────────────────────────────────────────────────┤
│  • ReliabilityAgent(corpus)     → RE01-RE10 evaluation         │
│  • SecurityAgent(corpus)        → SE01-SE12 evaluation         │
│  • CostAgent(corpus)            → CO01-CO14 evaluation         │
│  • OperationalAgent(corpus)     → OE01-OE11 evaluation         │
│  • PerformanceAgent(corpus)     → PE01-PE12 evaluation         │
└────────────────────────────────────────────────────────────────┘
    ↓
[Pillar Results Collection]
    ↓
[Aggregate Overall Architecture Score] = Average of 5 pillar scores
    ↓
[Return Assessment Object]
```

### Individual Pillar Agent Process

Each agent follows the same evaluation pattern:

#### Step 1: Concept Detection (Conservative Scoring)
- **Load Expected Concepts**: Each pillar has a curated catalog (e.g., Reliability: `backup`, `geo-replication`, `health-probe`, `circuit-breaker`)
- **Search Corpus**: Case-insensitive keyword matching
- **Calculate Coverage**:
  ```
  concept_coverage = (concepts_found / total_expected_concepts) * 100
  ```
- **Density Scoring**: Repeated mentions increase confidence
  - Single mention: Base weight
  - 2-3 mentions: 1.5x weight
  - 4+ mentions: 2x weight
- **Confidence Level**:
  - Low: <40% concept coverage
  - Medium: 40-70%
  - High: >70%

#### Step 2: LLM-Based Subcategory Assessment
- **Prompt Construction**: Agent sends corpus + pillar-specific instructions to Azure OpenAI
- **Subcategory Scoring**: LLM evaluates each subcategory (e.g., Reliability: `Backup Strategy`, `Disaster Recovery`, `High Availability`, etc.)
  - Scores 0-100 based on evidence in corpus
  - Applies `NO_EVIDENCE_SUBCATEGORY_FLOOR` (default 2) when no evidence found
  - Considers support case patterns as negative signals
- **Recommendation Generation**: LLM produces prioritized recommendations with:
  - Title & description
  - Priority (Critical / High / Medium / Low)
  - Affected services
  - Implementation steps
  - Estimated effort and timeline

#### Step 3: Multi-Section Scoring (Deterministic)
If multiple artifact types exist, agent calculates section-wise maturity:

**Section Weights**:
- **Architecture Narrative**: 40% (from docs, `raw_text`)
- **Diagram Analysis**: 30% (from `diagram_summary`)
- **Support Case History**: 20% (from `support_cases_summary`)
- **Consolidated Evidence**: 10% (synthesized insights)

Each section receives a 0-100 maturity score, then:
```
pillar_score = weighted_average(section_scores)
```

This provides deterministic scoring when multiple evidence sources are present.

#### Step 4: Result Packaging
Agent returns:
```json
{
  "pillar": "Reliability",
  "subcategories": {
    "Backup Strategy": 68,
    "Disaster Recovery": 45,
    "High Availability": 72,
    "Fault Tolerance": 55,
    "Monitoring & Observability": 80
  },
  "recommendations": [...],
  "confidence": "medium",
  "concept_coverage_percent": 62
}
```

### LLM Provider Fallback Strategy

The system supports **dual Azure LLM providers** with graceful degradation:

**Priority 1: Azure OpenAI** (if configured)
```python
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    client = AsyncAzureOpenAI(endpoint, api_key, api_version)
    # Use for diagram vision, subcategory analysis, recommendations
```

**Priority 2: Azure AI Foundry** (future integration)
```python
# Placeholder for Azure AI Foundry agent framework integration
# Will use MAF (Microsoft Agent Framework) when available
```

**Fallback: Static Templates** (no credentials)
```python
# Generate deterministic stub scores based on:
# - Concept coverage percentage
# - Document count heuristics
# - Support case severity distribution
# Ensures system remains functional for demos/testing
```

**Rate Limiting & Concurrency**:
- Concurrent LLM requests limited by asyncio semaphore (configurable)
- Exponential backoff on rate limit errors (429)
- Request timeout: 60 seconds default

### Caching & Performance

- **Embedding Cache**: Support case theme embeddings cached to avoid recomputation
- **Corpus Reuse**: Same corpus shared across all 5 agents (single assembly)
- **Parallel Execution**: All pillars evaluated concurrently (5-15 sec typical)

## 6. Scoring Methodology

The platform has evolved through three scoring generations, each building on the previous:

### Generation 1: Conservative Evidence-Based Scoring

**Philosophy**: Scores must be proportional to documentation depth and evidence quality.

**Key Mechanisms**:
- **Concept Coverage**: Pillar-specific expected concepts catalog
  - Example (Reliability): `["backup", "geo-replication", "health-probe", "circuit-breaker", "retry-policy", ...]`
  - Score penalty if concepts missing
- **Density Bonuses**: Repeated mentions signal intentional design
- **Confidence Levels**: 
  - High (>70% concepts): Green badge, full LLM evaluation
  - Medium (40-70%): Yellow badge, partial evaluation
  - Low (<40%): Red badge, capped score with warnings
- **Penalties**:
  - Missing critical concepts: -10 to -20 points per category
  - No disaster recovery plan: -15 points
  - No monitoring mentioned: -10 points

**Outcome**: Prevents inflated scores from sparse documentation, but scores could still exceed 100 when subcategories summed.

**Reference**: `docs/CONSERVATIVE_SCORING.md`

### Generation 2: Transparent Bottom-Up Scoring

**Philosophy**: Pillar scores should be the **sum of subcategory scores**, not top-down normalized.

**Changes**:
1. **Bottom-Up Calculation**:
   ```
   pillar_score = sum(subcategory_scores)
   ```
2. **Conditional Normalization**:
   - If `pillar_score ≤ 100`: No adjustment
   - If `pillar_score > 100`: Scale down to 100, set `normalization_applied = true`
3. **New Fields**:
   - `raw_subcategory_sum`: Original sum before normalization
   - `normalization_applied`: Boolean flag
   - `gap_based_recommendations`: Points recoverable if gaps addressed

**Example**:
```json
{
  "pillar": "Reliability",
  "subcategories": {
    "Backup Strategy": 22,
    "Disaster Recovery": 24,
    "High Availability": 31,
    "Monitoring": 27,
    "Testing": 27
  },
  "raw_subcategory_sum": 131,
  "normalization_applied": true,
  "overall_score": 100,
  "gap_based_recommendations": [
    {
      "title": "Address 31 Points of Hidden Gaps",
      "points_recoverable": 31,
      "priority": "High"
    }
  ]
}
```

**Outcome**: Full transparency—users see the "true" maturity (131 points) and understand the 31-point gap to perfection.

**Reference**: `docs/TRANSPARENT_SCORING_IMPLEMENTATION.md`

### Generation 3: Multi-Section Deterministic Scoring

**Philosophy**: When multiple artifact types exist (docs + diagrams + support cases), score each section independently then aggregate.

**Section Scoring**:

| Section | Weight | Evidence Source |
|---------|--------|-----------------|
| Architecture Narrative | 40% | `raw_text`, architecture docs |
| Diagram Analysis | 30% | `diagram_summary`, visual components |
| Support Case History | 20% | `support_cases_summary`, incident patterns |
| Consolidated Evidence | 10% | Synthesized insights from all sources |

Each section receives a 0-100 maturity score from LLM based on evidence quality:
- **Immature (0-40)**: Missing critical practices
- **Developing (41-60)**: Basic practices present
- **Mature (61-80)**: Strong practices with gaps
- **Optimized (81-100)**: Comprehensive best practices

**Final Pillar Score**:
```
pillar_score = (0.4 × narrative_score) + (0.3 × diagram_score) + 
               (0.2 × support_case_score) + (0.1 × consolidated_score)
```

**Advantages**:
- Deterministic (same inputs → same scores)
- Rewards comprehensive documentation
- Penalizes single-source architectures
- Support case history provides real-world validation

**Reference**: `docs/MULTI_SECTION_SCORING.md`

### Normalization & Gap Analysis

When subcategories sum exceeds 100:

**Before Normalization** (raw truth):
```
Backup Strategy:     22 points
Disaster Recovery:   24 points
High Availability:   31 points
Monitoring:          27 points
Testing:             27 points
────────────────────────────
Raw Sum:            131 points  ← True maturity level
```

**After Normalization** (UI display):
```
Overall Score: 100 points
Gap: 31 points recoverable
```

**Gap Recommendation Generated**:
```
Title: "Address 31 Points of Hidden Gaps to Achieve True Maturity"
Priority: High
Description: Your Reliability subcategories sum to 131 points, indicating 
maturity beyond the normalized 100-point scale. Addressing architectural 
gaps in backup redundancy, geo-replication consistency, and health probe 
coverage can unlock this hidden potential.
```

### Rescoring Existing Assessments

Assessments created before transparent scoring can be **rescored** to apply new methodology:

**API Endpoints**:
```bash
# Rescore single assessment
POST /api/assessments/{assessment_id}/rescore

# Rescore all assessments
POST /api/assessments/rescore-all
```

**Script Interface**:
```bash
python scripts/rescore_existing_assessments.py --list
python scripts/rescore_existing_assessments.py <assessment_id>
python scripts/rescore_existing_assessments.py --all
```

**What Changes**:
- Subcategory structure preserved (same LLM-generated names)
- Pillar score recalculated as sum (not top-down normalized)
- Normalization flags added
- Gap-based recommendations appended
- Original scores archived in `score_history` (non-destructive)

**Reference**: `docs/RESCORING_GUIDE.md`

## 7. Recommendations Generation

Recommendations are produced during LLM analysis and enhanced by gap analysis.

### LLM-Generated Recommendations

Each pillar agent prompts Azure OpenAI to produce recommendations based on:
- **Missing Concepts**: Critical practices not found in corpus
- **Support Case Patterns**: Recurring failures suggesting weaknesses
- **Best Practice Gaps**: Deviations from Well-Architected Framework
- **Architecture Risks**: Single points of failure, scaling limits, security exposures

**Recommendation Structure**:
```json
{
  "title": "Implement Multi-Region Disaster Recovery",
  "description": "Architecture lacks cross-region redundancy. Single region failure would cause complete outage.",
  "priority": "Critical",
  "affected_services": ["Azure App Service", "Azure SQL Database"],
  "implementation_steps": [
    "Deploy secondary region (e.g., East US 2)",
    "Configure Azure Traffic Manager with priority routing",
    "Setup geo-replication for Azure SQL Database",
    "Implement data sync strategy for Storage Accounts",
    "Test failover procedures quarterly"
  ],
  "effort_estimate": "High (6-8 weeks)",
  "estimated_cost_impact": "Medium (+20-30% infrastructure)",
  "azure_services_required": ["Traffic Manager", "SQL Geo-Replication"],
  "timeframe": "Medium-term (3-6 months)"
}
```

### Gap-Based Recommendations

When normalization occurs (`raw_subcategory_sum > 100`), system generates **gap recovery recommendations**:

**Gap Analysis**:
```
Gap = raw_subcategory_sum - 100
Example: 131 - 100 = 31 points
```

**Generated Recommendation**:
```json
{
  "title": "Address 31 Points of Hidden Gaps to Achieve True Maturity",
  "priority": "High",
  "points_recoverable": 31,
  "reasoning": "Your Reliability subcategories sum to 131 points, indicating maturity beyond the 100-point normalized scale. This 31-point gap represents areas where architectural improvements can elevate true reliability.",
  "focus_areas": [
    "Backup Strategy: Implement cross-region backup replication",
    "Disaster Recovery: Reduce RTO from 4h to <1h target",
    "High Availability: Add zone redundancy for all critical services"
  ]
}
```

### Recommendation Prioritization

**Priority Levels**:
- **Critical**: Immediate risk to availability, security, or compliance (Red badge)
- **High**: Significant improvement opportunity, medium-term action (Orange badge)
- **Medium**: Best practice enhancement, long-term planning (Yellow badge)
- **Low**: Optimization opportunity, nice-to-have (Blue badge)

**Sorting Algorithm**:
1. Priority level (Critical → High → Medium → Low)
2. Estimated impact score (0-10)
3. Effort estimate (Low effort prioritized for quick wins)

### Cohesive Cross-Pillar Recommendations

When multiple pillars detect related issues, system generates **cohesive recommendations** that address concerns holistically:

**Example Conflict**:
- **Reliability Agent**: "Add zone redundancy" (increases availability)
- **Cost Agent**: "Right-size VM SKUs" (reduces spend)

**Cohesive Recommendation**:
```
Title: "Balance Zone Redundancy with Cost Optimization"
Description: Deploy zone-redundant App Service Plan (S1 tier) instead of 
P1V2 to achieve 99.95% SLA while reducing monthly cost by $150.
Impacted Pillars: Reliability, Cost Optimization
```

These appear in a dedicated **"Cohesive Recommendations"** section in the UI (collapsible panel).

## 8. Visualization & UI

The frontend provides comprehensive visualization of assessment results with interactive components and transparency indicators.

### Core UI Components

#### 1. Upload Documents Tab
- **Drag-and-drop** file upload
- **Real-time thumbnails** (80×80) for all uploaded files
- **Document metadata** display:
  - Filename, size, upload timestamp
  - Category (Architecture, Diagram, Support Cases, PDF)
  - Enrichment status badges
- **Delete functionality** with confirmation
- **Supported formats**: `.txt`, `.md`, `.docx`, `.pdf`, `.csv`, `.svg`, `.png`, `.jpg`

#### 2. Analysis Progress Tab
- **Real-time progress tracking** via WebSocket polling
- **Phase indicators**:
  - Document Upload (Green checkmark when complete)
  - Enrichment Pipeline (animated during processing)
  - Corpus Assembly (with document count)
  - Pillar Analysis (5 concurrent progress bars)
  - Scoring & Recommendations (final aggregation)
- **Collapsible panels** (default closed):
  - **Cohesive Recommendations**: Cross-pillar insights
  - **Assessment Phase Details**: Expanded logs, timestamps, agent activity
- **Toggle arrows** (▼ / ▶) for expand/collapse

#### 3. Results Scorecard Tab
- **Overall Architecture Score** (large metric, 0-100 scale)
- **5 Pillar Score Cards**:
  ```
  ┌─────────────────────────────────────┐
  │ Reliability                    72   │
  │ ████████████████░░░░░░░░      72%   │
  │ Confidence: Medium  📊             │
  │ [View Details ▼]                    │
  └─────────────────────────────────────┘
  ```
- **Confidence Badges**:
  - 🟢 High (>70% concept coverage)
  - 🟡 Medium (40-70%)
  - 🔴 Low (<40%)
- **Expandable sections** per pillar:
  - Subcategory scores (bar chart or table)
  - Top 5 recommendations
  - Normalization disclosure (if applied)

#### 4. Hidden Gap Analysis Panel
Appears **only when normalization applied** to any pillar:

```
┌────────────────────────────────────────────────────────────────┐
│ ⚠️ Score Normalization Applied                                │
│                                                                │
│ Some pillar scores were normalized to fit the 0-100 scale.    │
│ The gaps below represent areas where your architecture could   │
│ improve beyond the normalized score.                           │
│                                                                │
│ Reliability                                                    │
│   Normalized from 131 → 100                                   │
│   Gap: 31 points recoverable                                  │
│                                                                │
│ Recommendations to recover 31 points:                         │
│   • [High] Address 31 Points of Hidden Gaps to Achieve True   │
│     Maturity (Est. 8-12 weeks)                                │
│                                                                │
│ Security                                                       │
│   Normalized from 118 → 100                                   │
│   Gap: 18 points recoverable                                  │
│   ...                                                          │
└────────────────────────────────────────────────────────────────┘
```

**Styling**:
- Yellow warning background (`#FFF4E6`)
- Orange border left accent
- Collapsible (default expanded if gaps exist)

#### 5. Recommendations List
- **Sorted by priority** (Critical → High → Medium → Low)
- **Color-coded badges**:
  - Critical: `#DC2626` (dark red)
  - High: `#EA580C` (orange)
  - Medium: `#F59E0B` (amber)
  - Low: `#3B82F6` (blue)
- **Expandable cards** showing:
  - Title & description
  - Affected services (pills)
  - Implementation steps (numbered list)
  - Effort & timeline estimates
  - Cost impact indicator
- **Filter toggles**: Show/hide by priority level

#### 6. Visualization Charts

**Pillar Comparison Radar Chart** (Recharts):
```
         Reliability
              100
               /\
              /  \
    Cost ___/____\___ Security
         \      /
          \    /
           \  /
            \/
      Operational
```
- Interactive hover tooltips
- Concept coverage overlay (dashed line)
- Normalization indicators (asterisk on normalized pillars)

**Subcategory Breakdown Bar Chart**:
```
Backup Strategy          ████████████░░░░░░░░  68
Disaster Recovery        █████████░░░░░░░░░░░  45
High Availability        ██████████████░░░░░░  72
Fault Tolerance          ██████████░░░░░░░░░░  55
Monitoring               ████████████████░░░░  80
```
- Horizontal bars (0-100 scale)
- Color gradient based on maturity level
- Click to expand subcategory details

**Confidence Distribution Pie Chart**:
```
   High: 2 pillars (40%)
 Medium: 2 pillars (40%)
    Low: 1 pillar (20%)
```

### Excel Export

**Multi-sheet workbook** generated via XLSX.js:

**Sheet 1: Summary**
- Overall score
- Pillar scores (with normalization flags)
- Assessment metadata (date, documents, status)

**Sheet 2: Detailed Scores**
- All subcategories across pillars
- Raw sums vs normalized (if applicable)
- Confidence levels

**Sheet 3: Recommendations**
- Full recommendation list
- Priority, effort, cost, timeline
- Implementation steps

**Export button** in header:
```typescript
const exportToExcel = () => {
  const wb = XLSX.utils.book_new();
  // Add sheets...
  XLSX.writeFile(wb, `assessment_${assessmentId}_${timestamp}.xlsx`);
};
```

### Real-Time Updates

Frontend uses **polling mechanism** (every 2 seconds during analysis):
```typescript
const pollAssessment = async () => {
  const response = await fetch(`/api/assessments/${id}`);
  const assessment = await response.json();
  
  if (assessment.status === 'completed') {
    clearInterval(pollInterval);
    showResults();
  }
  
  updateProgress(assessment.progress);
};
```

Alternative: WebSocket support (planned future enhancement for live agent logs).

### Responsive Design

- **Desktop**: 3-column layout (upload | progress | results)
- **Tablet**: 2-column with tab navigation
- **Mobile**: Single-column stacked, collapsible panels

**Accessibility**:
- ARIA labels on all interactive elements
- Keyboard navigation (Tab, Enter, Space)
- High contrast mode support
- Screen reader compatible

### UI Component Library

- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS 3
- **Charts**: Recharts 2.x
- **Icons**: Lucide React
- **Tables**: Tanstack Table (for sortable columns)
- **Exports**: XLSX.js (SheetJS)

## 9. API Usage

### REST Endpoints

#### Create Assessment
```bash
POST /api/assessments
Content-Type: application/json

{
  "name": "Production Web App Review",
  "description": "Q4 2025 architecture assessment"
}

Response:
{
  "id": "assess_1234567890",
  "name": "Production Web App Review",
  "status": "created",
  "created_at": "2025-11-09T10:30:00Z"
}
```

#### Upload Documents
```bash
POST /api/assessments/{assessment_id}/documents
Content-Type: multipart/form-data

files: [architecture.md, diagram.svg, cases.csv]
category: architecture  # or diagram, support_cases

Response:
{
  "documents": [
    {
      "id": "doc_001",
      "filename": "architecture.md",
      "thumbnail_url": "data:image/png;base64,...",
      "enrichment_status": "completed"
    },
    ...
  ]
}
```

#### Start Analysis
```bash
POST /api/assessments/{assessment_id}/analyze

Response:
{
  "status": "analyzing",
  "progress": 0,
  "current_phase": "corpus_assembly"
}
```

#### Get Assessment Results
```bash
GET /api/assessments/{assessment_id}

Response:
{
  "id": "assess_1234567890",
  "status": "completed",
  "overall_architecture_score": 72.4,
  "pillar_scores": {
    "reliability": {
      "overall_score": 72,
      "raw_subcategory_sum": 131,
      "normalization_applied": true,
      "subcategories": {...},
      "recommendations": [...],
      "gap_based_recommendations": [...]
    },
    ...
  },
  "completed_at": "2025-11-09T10:45:00Z"
}
```

#### Rescore Assessment (Transparent Upgrade)
```bash
POST /api/assessments/{assessment_id}/rescore

Response:
{
  "message": "Assessment rescored successfully",
  "changes": {
    "reliability": {
      "old_score": 100,
      "new_score": 100,
      "raw_subcategory_sum": 131,
      "normalization_applied": true,
      "gap_recommendations_added": 1
    }
  }
}
```

### Python SDK Usage

```python
import asyncio
from backend.app.agents.reliability_agent import ReliabilityAgent

async def assess_architecture():
    agent = ReliabilityAgent(
        assessment_mode="comprehensive",
        enable_mcp=True  # Enable MCP documentation access
    )
    
    architecture = """
    E-commerce platform:
    - Azure App Service (Standard tier, single region)
    - Azure SQL Database (DTU-based, no geo-replication)
    - Azure Storage (LRS redundancy)
    - Application Insights (basic monitoring)
    """
    
    result = await agent.assess_architecture_reliability(
        architecture_content=architecture,
        business_criticality="high",
        compliance_requirements="PCI-DSS, SOC2"
    )
    
    print(f"Overall Score: {result.overall_reliability_score}/100")
    print(f"Confidence: {result.confidence}")
    print(f"Top Recommendation: {result.recommendations[0].title}")
    
    return result

# Run assessment
assessment = asyncio.run(assess_architecture())
```

### CLI Usage

```bash
# Reliability pillar only
python -m src.app.agents.reliability_agent architecture.txt

# With support cases
python -m src.app.agents.reliability_agent architecture.txt \
  --cases sample_data/azure_support_cases.csv

# All pillars via orchestrator
python scripts/run_full_assessment.py architecture.txt \
  --output results/full_assessment.json
```

## 10. Testing

```bash
# Run all tests
pytest -vv -s

# Specific test suites
pytest tests/test_api_direct_create.py -v              # API contract
pytest tests/test_conservative_scoring.py -v           # Scoring logic
pytest tests/test_api_persistence.py -v                # MongoDB integration

# Coverage report
pytest --cov=backend --cov-report=html
```

**Test Structure**:
- `tests/test_api_*.py` – API endpoint validation
- `tests/test_*_scoring.py` – Scoring algorithm correctness
- `tests/test_*_agent_e2e.py` – End-to-end pillar evaluation
- `tests/conftest.py` – Shared fixtures (mock LLM, test corpus)

## 11. Advanced Configuration

### Environment Variables

**LLM Provider** (choose one):
```bash
# Azure OpenAI (recommended)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Foundry (future)
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

**Scoring Tunables**:
```bash
CASE_SUMMARY_MAX_CASES=25                # Max support case bullets
NO_EVIDENCE_SUBCATEGORY_FLOOR=2          # Min score when no evidence
USE_CURATED_EXPECTED_CONCEPTS=true       # Use concept catalogs
```

**Persistence**:
```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=wara_assessments
```

**Rate Limiting**:
```bash
AZURE_OPENAI_MAX_CONCURRENT_REQUESTS=5   # Concurrency limit
AZURE_OPENAI_RETRY_MAX_ATTEMPTS=3        # Retry on 429/500
```

**Tracing** (see `docs/TRACING_DIAGNOSTICS.md`):
```bash
AZURE_AI_FOUNDRY_TRACING_ENABLED=true
LOG_LEVEL=INFO                           # DEBUG for verbose
```

### Concept Catalog Customization

Edit `backend/utils/concepts.py` to adjust expected concepts per pillar:

```python
RELIABILITY_CONCEPTS = [
    "backup", "geo-replication", "availability-zone",
    "health-probe", "circuit-breaker", "retry-policy",
    "disaster-recovery", "rto", "rpo", "failover",
    # Add custom concepts here
]
```

### Scoring Formula Adjustments

**Conservative penalty tuning** (`backend/app/analysis/scoring.py`):
```python
MISSING_DR_PENALTY = -15        # Default -15
MISSING_MONITORING_PENALTY = -10
DENSITY_BONUS_THRESHOLD = 3     # Mentions needed for bonus
```

**Normalization threshold** (`backend/server.py`):
```python
NORMALIZATION_THRESHOLD = 100   # Apply scaling if sum > this
```

## 12. Documentation Index

| Document | Purpose |
|----------|---------|
| `docs/CONSERVATIVE_SCORING.md` | Evidence-based scoring with concept coverage |
| `docs/TRANSPARENT_SCORING_IMPLEMENTATION.md` | Bottom-up summation + normalization disclosure |
| `docs/MULTI_SECTION_SCORING.md` | Deterministic section-wise maturity model |
| `docs/NORMALIZATION_MIGRATION.md` | Schema changes for transparency |
| `docs/RESCORING_GUIDE.md` | Steps to upgrade legacy assessments |
| `docs/AZURE_OPENAI_INTEGRATION.md` | LLM provider setup + fallback strategy |
| `docs/TRACING_DIAGNOSTICS.md` | Observability + troubleshooting |
| `docs/DIAGRAM_VISION_FIX.md` | Diagram extraction improvements |
| `docs/ENHANCED_DIAGRAM_ANALYSIS_READY.md` | Enrichment pipeline deep-dive |
| `docs/MONGODB_SETUP.md` | Persistence configuration |
| `docs/MONGODB_PERSISTENCE_COMPLETE.md` | Persistence feature completion |
| `docs/DEV_SETUP.md` | Developer environment + run scripts |
| `docs/VISUALIZATION_GUIDE.md` | Chart architecture + UI patterns |
| `docs/MIGRATION_SUMMARY.md` | `src/` → `backend/` package migration |

## 13. Contributing

Contributions welcome! Focus areas:

- **Scoring Refinements**: Adjust penalties, thresholds, concept catalogs
- **New Pillars**: Expand Performance Efficiency (PE01-PE12) coverage
- **Visualization**: Advanced charts (trend analysis, heat maps)
- **Integrations**: CI/CD pipeline plugins, Terraform export
- **Performance**: Batch inference, caching strategies

**Development Workflow**:
```bash
git checkout -b feature/your-feature
# Make changes
pytest -vv
git commit -m "feat: your feature description"
git push origin feature/your-feature
# Open pull request
```

## 14. License

MIT License – see `LICENSE` file.

---

## Quick Command Reference

```bash
# Backend
python -m uvicorn backend.server:app --reload --port 8000

# Frontend
cd frontend && npm run dev

# Rescore all assessments
python scripts/rescore_existing_assessments.py --all

# Run full test suite
pytest -vv --cov=backend

# Generate concept coverage report
python scripts/analyze_cost_scoring.py results/cost_optimization_assessment.json
```

For production deployment, monitoring, and security hardening, see planned `docs/DEPLOYMENT.md` (coming soon).

**Ready to assess your Azure architecture? Start with [Quick Setup](#2-quick-setup) above.**



