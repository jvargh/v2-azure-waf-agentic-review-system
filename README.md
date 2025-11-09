# Azure Well-Architected Framework Reliability Agent

🛡️ **Enterprise-grade Azure reliability assessment using Microsoft Agent Framework with real-time documentation integration.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Azure](https://img.shields.io/badge/Azure-Cloud-0078d4.svg)](https://azure.microsoft.com)
[![MAF](https://img.shields.io/badge/Microsoft_Agent_Framework-Latest-orange.svg)](https://github.com/microsoft/agent-framework)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

The **Azure Well-Architected Framework Reliability Agent** is an intelligent, enterprise-grade solution designed to assess and optimize Azure infrastructure for reliability best practices. Built on the **Microsoft Agent Framework (MAF)** with **Model Context Protocol (MCP)** integration, this agent provides comprehensive, real-time reliability assessments that align with Microsoft's Well-Architected Framework principles.

### 🏗️ What Makes This Special

- **🤖 AI-Powered Assessment**: Uses Azure AI Foundry GPT-4.1 for intelligent analysis
- **📚 Real-Time Documentation**: MCP integration provides access to latest Azure docs
- **🔍 Comprehensive Analysis**: Covers all 5 reliability domains with weighted scoring
- **📊 Enterprise Reporting**: Structured JSON + human-readable outputs
- **⚡ String Input Processing**: Accepts architecture descriptions as simple text
- **🚀 Production Ready**: Built for enterprise environments and CI/CD integration

### 🧱 Pillar Coverage

- **Reliability Agent (`RE01`–`RE10`)** – Deep-dive on resiliency, redundancy, testing, and recovery.
- **Security Agent (`SE01`–`SE12`)** – Zero Trust assessment covering IAM, network isolation, data protection, monitoring, and incident response.
- **Cost Optimization Agent (`CO01`–`CO14`)** – FinOps practices covering cost modeling, monitoring, optimization, and financial accountability.

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [🏛️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Installation](#️-installation)
- [🔧 Configuration](#-configuration)
- [📖 Usage](#-usage)
- [🧪 Testing](#-testing)
- [📊 Assessment Output](#-assessment-output)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🏛️ Architecture

```
azure-well-architected-agents/
├── src/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── reliability_agent.py     # 🤖 Reliability pillar agent
│   │   │   ├── security_agent.py        # 🔐 Security pillar agent
│   │   │   └── cost_agent.py            # 💰 Cost Optimization pillar agent
│   │   └── tools/
│   │       └── mcp_tools.py             # 🔧 MCP documentation tools
│   ├── prompts/
│   │   ├── reliability_agent_instructions.txt
│   │   ├── security_agent_instructions.txt
│   │   └── cost_agent_instructions.txt
│   └── utils/
│       └── env_utils.py                 # 🌍 Environment configuration
├── tests/
│   ├── test_reliability_agent_e2e.py    # 🧪 Reliability tests
│   ├── test_security_agent_e2e.py       # 🧪 Security tests
│   └── test_cost_agent_e2e.py           # 🧪 Cost Optimization tests
├── requirements.txt                     # 📦 Python dependencies
└── README.md                           # 📚 This documentation
```

### 🔄 System Flow

1. **Input**: Architecture description as string
2. **Processing**: Microsoft Agent Framework + Azure AI Foundry
3. **Enhancement**: MCP tools access real-time Azure documentation
4. **Analysis**: 5-domain reliability assessment with weighted scoring
5. **Output**: Structured JSON + human-readable reports

## 🚀 Quick Start

### 1️⃣ Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd azure-well-architected-agents

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your Azure credentials
```

### 2️⃣ Configure Azure Services

```bash
# Set up Azure AI Foundry (Recommended)
export AZURE_AI_ENDPOINT="your-foundry-endpoint"
export AZURE_AI_MODEL_NAME="gpt-4"
export AZURE_AI_API_VERSION="2024-02-01"

# OR Azure OpenAI (Alternative)
export AZURE_OPENAI_ENDPOINT="your-openai-endpoint"  
export AZURE_OPENAI_API_KEY="your-api-key"
export AZURE_OPENAI_MODEL_NAME="gpt-4"
```

### 3️⃣ Run Assessment (Programmatic)

```python
import asyncio
from backend.app.agents.reliability_agent import ReliabilityAgent
from backend.app.agents.security_agent import SecurityAgent
from backend.app.agents.cost_agent import CostAgent
from backend.app.agents.operational_agent import OperationalAgent

async def main():
    # Your architecture description
    architecture = """
    E-commerce platform with Azure App Service, 
    SQL Database, and Storage Account. 
    Single region deployment in West US 2.
    No disaster recovery configured.
    """
    
    # Run Reliability assessment (RE01-RE10)
    reliability_agent = ReliabilityAgent(
        assessment_mode="comprehensive",
        enable_mcp=True
    )
    rel_assessment = await reliability_agent.assess_architecture_reliability(
        architecture_content=architecture,
        business_criticality="high",
        compliance_requirements="SOC2, PCI-DSS",
        rto_rpo_targets="RTO: 15min, RPO: 5min"
    )
    
    # Run Security assessment (SE01-SE12)
    security_agent = SecurityAgent()
    sec_assessment = await security_agent.assess_architecture(architecture)
    
    # Run Cost Optimization assessment (CO01-CO14)
    cost_agent = CostAgent()
    cost_assessment = await cost_agent.assess_architecture(architecture)
    
    # Run Operational Excellence assessment (OE01-OE11)
    operational_agent = OperationalAgent()
    ops_assessment = await operational_agent.assess_architecture(architecture)
    
    # View results
    print(f"Reliability Score: {rel_assessment.overall_reliability_score}/100")
    print(f"Security Maturity: {sec_assessment.maturity.get('overall_maturity_percent')}%")
    print(f"Cost Maturity: {cost_assessment.maturity.get('overall_maturity_percent')}%")
    print(f"Operational Maturity: {ops_assessment.maturity.get('overall_maturity_percent')}%")

if __name__ == "__main__":
    asyncio.run(main())
```

### 3️⃣ Alternative: Run from Command Line

Each agent can be invoked directly with an architecture file:

```bash
# Create an architecture description file
cat > my_architecture.txt << EOF
E-commerce platform with Azure App Service,
SQL Database, and Storage Account.
Single region deployment in West US 2.
No disaster recovery configured.
EOF

# Run Reliability Agent (RE01-RE10)
python -m src.app.agents.reliability_agent my_architecture.txt

# Run Security Agent (SE01-SE12)
python -m src.app.agents.security_agent my_architecture.txt

# Run Cost Optimization Agent (CO01-CO14)
python -m src.app.agents.cost_agent my_architecture.txt

# Run Operational Excellence Agent (OE01-OE11)
python -m src.app.agents.operational_agent my_architecture.txt

# Results are written to results/ directory by default

#### Including Historical Azure Support Cases

You can enrich any pillar assessment with real Azure support case history. Provide a CSV with columns:

`title, msdfm_productname, msdfm_customerstatement, msdfm_resolution`

Example invocation:

```bash
python -m src.app.agents.reliability_agent my_architecture.txt --cases data/azure_support_cases.csv
python -m src.app.agents.cost_agent my_architecture.txt --cases data/azure_support_cases.csv
```

These cases are summarized and appended to the architecture context under a markdown heading:
`### Historical Azure Support Cases (Context)` so the agent can derive recommendations influenced by real incidents and resolutions.
```

### 4️⃣ Run Test Suite

```bash
# Test the implementation
python test_reliability_agent.py
```

## ⚙️ Installation

### Prerequisites

- **Python 3.8+** (3.9+ recommended)
- **Azure Subscription** with AI services enabled
- **Azure AI Foundry** or **Azure OpenAI** access
- **Valid Azure credentials** (Service Principal, Managed Identity, or Azure CLI)

### Step-by-Step Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core requirements
pip install -r requirements.txt

# Optional: Install development tools
pip install black mypy pytest-cov
```

## 🔧 Configuration

### Step 1: Set up Azure LLM Service

**Choose ONE option:**

#### Option A: Azure AI Foundry (Recommended)
1. Create Azure AI Foundry resource in Azure portal
2. Deploy a GPT model (e.g., gpt-4o-mini)
3. Note your project endpoint

#### Option B: Azure OpenAI (Direct)
1. Create Azure OpenAI resource in Azure portal  
2. Deploy a GPT model (e.g., gpt-4o-mini)
3. Note your endpoint and API key

### Step 2: Configure Environment Variables

Create a `.env` file from the template:

```bash
# Copy the template
cp .env.template .env

# Edit the .env file with your values
```

**For Azure AI Foundry:**
```bash
AZURE_AI_PROJECT_ENDPOINT=https://your-ai-foundry-name.services.ai.azure.com
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini
```

**For Azure OpenAI:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
```

### Step 3: Authenticate with Azure

```bash
# Install Azure CLI if needed
az login

# Verify you can access your Azure resources
az account show
```
MCP_TIMEOUT=30
```

## 📖 Usage

### Basic Usage

```python
import asyncio
from backend.app.agents.reliability_agent import ReliabilityAgent

async def basic_assessment():
    agent = ReliabilityAgent()
    
    architecture = "Azure App Service with SQL Database, no backup configured"
    
    assessment = await agent.assess_architecture_reliability(
        architecture_content=architecture
    )
    
    return assessment

# Run the assessment
result = asyncio.run(basic_assessment())
print(f"Score: {result.overall_reliability_score}/100")
```

#### Running the Security Agent

```python
import asyncio
from backend.app.agents.security_agent import SecurityAgent


async def assess_security():
  agent = SecurityAgent(enable_mcp=True)
  architecture = "Azure App Service with public endpoints and secrets in app settings"
  assessment = await agent.assess_architecture(architecture)
  print(f"Security Score: {assessment.overall_score}/100")


asyncio.run(assess_security())
```

### Advanced Configuration

```python
# Comprehensive assessment with MCP integration
agent = ReliabilityAgent(
    assessment_mode="comprehensive",  # Options: quick_assessment, comprehensive, deep_dive
    enable_mcp=True                   # Enable real-time Azure docs access
)

# Enterprise assessment with compliance requirements
assessment = await agent.assess_architecture_reliability(
    architecture_content=architecture_description,
    business_criticality="mission_critical",    # low, medium, high, mission_critical
    compliance_requirements="SOC2, PCI-DSS, HIPAA",
    rto_rpo_targets="RTO: 15min, RPO: 1min"
)
```

### Assessment Modes

| Mode | Description | Use Case | Duration |
|------|-------------|----------|----------|
| `quick_assessment` | Fast overview with top 3 issues | Initial screening | 2-5 minutes |
| `comprehensive` | Full 5-domain analysis | Standard enterprise assessment | 5-15 minutes |
| `deep_dive` | Detailed analysis with implementation plans | Critical system assessment | 15-30 minutes |

## 🧪 Testing

Run all tests with verbose names and live assertion logging:

```bash
pytest -vv -s
```

Targeted test runs (one agent at a time):

```bash
# Reliability pillar tests (RE01-RE10)
python -m pytest tests/test_reliability_agent_e2e.py -v

# Security pillar tests (SE01-SE12)
python -m pytest tests/test_security_agent_e2e.py -v

# Cost Optimization pillar tests (CO01-CO14)
python -m pytest tests/test_cost_agent_e2e.py -v

# Operational Excellence pillar tests (OE01-OE11)
python -m pytest tests/test_operational_agent_e2e.py -v

# Performance Efficiency pillar tests (PE01-PE12) - coming soon
# python -m pytest tests/test_performance_agent_e2e.py -v

# Run all agent tests
python -m pytest tests/ -v -k "agent_e2e"

# Run all tests (including MCP tools)
python -m pytest tests/ -v
```


## 📊 Assessment Output

### Reliability Domains Assessed

1. **High Availability (25% weight)** - Multi-zone deployments, load balancing, redundancy
2. **Disaster Recovery (25% weight)** - Cross-region replication, backup strategies, RTO/RPO alignment
3. **Fault Tolerance (20% weight)** - Circuit breakers, retry mechanisms, graceful degradation
4. **Backup & Restore (15% weight)** - Data protection, point-in-time recovery, testing procedures
5. **Monitoring & Observability (15% weight)** - Health monitoring, alerting, auto-remediation

### Output Files Generated
All assessment artifacts are written to the `results/` directory by default.

Reliability:
- **`reliability_assessment.json`** – Structured assessment data for programmatic use
- **`reliability_assessment.md`** – Human-readable report for stakeholders

Cost Optimization:
- **`cost_optimization_assessment.json`** – Structured cost pillar scoring + recommendations
- **`cost_optimization_assessment.md`** – Markdown report with domain scores (CO01–CO14) and prioritized FinOps actions

Security (when executed via CLI once persistence is added):
- **`security_assessment.json`** – Scored security practices and maturity indicators (SE01–SE12)
- **`security_assessment.md`** – Markdown narrative (pending persistence addition)

Operational Excellence (planned for persistence):
- **`operational_assessment.json`** / **`operational_assessment.md`** (OE01–OE11) – Coming soon

Performance Efficiency (scaffolded – pending full implementation):
- **`performance_assessment.json`** / **`performance_assessment.md`** (PE01–PE12) – Coming soon

### Sample Assessment Results

```json
{
  "overall_reliability_score": 45,
  "domain_scores": {
    "high_availability": 30,
    "disaster_recovery": 20, 
    "fault_tolerance": 50,
    "backup_restore": 40,
    "monitoring_observability": 60
  },
  "critical_findings": [
    {
      "title": "Single Region Deployment Risk",
      "severity": "critical",
      "description": "Architecture deployed in single region creates significant availability risk",
      "affected_services": ["App Service", "SQL Database"],
      "business_impact": "Complete service outage during regional failures",
      "category": "high_availability"
    }
  ],
  "recommendations": [
    {
      "title": "Implement Multi-Region Architecture",
      "description": "Deploy application across multiple Azure regions with traffic manager",
      "priority": 1,
      "effort_estimate": "high",
      "impact_score": 9,
      "implementation_steps": [
        "Setup secondary region",
        "Configure Traffic Manager", 
        "Implement geo-replication"
      ],
      "azure_services_required": ["Traffic Manager", "Geo-replicated SQL"],
      "estimated_cost_impact": "medium",
      "timeframe": "medium-term"
    }
  ]
}
```

## 🛠️ Development

### Project Structure

- **`src/app/agents/reliability_agent.py`** - Main agent implementation with MAF integration
- **`src/app/tools/mcp_tools.py`** - MCP tools for real-time Azure documentation access
- **`src/prompts/reliability_prompts.py`** - AI prompts and assessment templates
- **`src/utils/env_utils.py`** - Environment configuration and credential management
- **`test_reliability_agent.py`** - Comprehensive test suite

### Key Features

- **Microsoft Agent Framework Integration** - Uses MAF for enterprise-grade AI interactions
- **Model Context Protocol (MCP)** - Real-time access to Azure documentation
- **Conservative Evidence-Based Scoring** - Scores proportional to documentation depth with confidence metrics (see [CONSERVATIVE_SCORING.md](CONSERVATIVE_SCORING.md))
- **Async/Await Pattern** - Non-blocking operations for enterprise scalability
- **Structured Output** - JSON schema validation for consistent results
- **Multi-Mode Assessment** - Flexible depth based on requirements
- **Cross-Pillar Integration** - Provides constraints for other WAF agents
- **Confidence Transparency** - Low/Medium/High confidence indicators based on evidence quality

## 🤝 Contributing

We welcome contributions! Areas for enhancement:

- 🐛 **Bug Fixes** - Help us identify and resolve issues
- 📈 **Performance Improvements** - Optimize assessment speed and accuracy  
- 🔧 **New Features** - Add new assessment domains or capabilities
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Expand test coverage and scenarios
- 🌐 **Integration** - Add support for new Azure services

### Development Workflow

1. Fork and clone the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make changes following code standards
4. Run tests: `python test_reliability_agent.py`
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **📖 Documentation**: This README and inline code comments
- **🐛 Issues**: Report bugs with detailed reproduction steps  
- **💡 Discussions**: Use GitHub Discussions for questions
- **🚀 Enterprise Support**: Contact for production deployments

---

**🎯 Ready to assess your Azure reliability?**

Start with the Quick Start guide above, or run `python test_reliability_agent.py` to see the agent in action!

## 📚 Documentation Index (Relocated)

Project documentation has been moved into the `docs/` folder for a cleaner root.

| Doc | Purpose |
|-----|---------|
| `docs/CONSERVATIVE_SCORING.md` | Detailed conservative evidence-based scoring implementation |
| `docs/SCORING_TUNING_GUIDE.md` | How to adjust scoring strictness (penalties, gates, bonuses) |
| `docs/MIGRATION_SUMMARY.md` | Summary of migration from `src/` to `backend/` package |
| `docs/IMPLEMENTATION_COMPLETE.md` | Full feature implementation checklist & architecture overview |
| `docs/DEV_SETUP.md` | Developer environment setup & run scripts |
| `docs/TRACING_DIAGNOSTICS.md` | Azure AI Foundry tracing & observability troubleshooting |
| `docs/CONVERTING_DOCS.md` | Converting `.docx` files to Markdown for version control |

Test and validation scripts relocated:

| New Location | Examples |
|--------------|----------|
| `tests/` | `test_api_direct_create.py`, `test_conservative_scoring.py`, `test_scoring_context.py` |
| `scripts/` | `apply_scoring_breakdown.py`, `analyze_cost_scoring.py`, `compare_support_cases.py`, `validate_strict_scoring.py` |

Update any bookmarks or automation referencing old root paths accordingly.

---

## 📦 Artifact Enrichment

Uploaded artifacts are enriched with explicit structured fields during the document ingestion phase:

| Artifact | Fields | Fallback | Structured Report |
|----------|--------|----------|-------------------|
| Architecture Docs | `raw_text`, `analysis_metadata.structured_report` | Heuristic sentence cleanse if analyzer error | Yes |
| Diagrams (SVG/PNG/JPG) | `raw_extracted_text`, `diagram_summary`, `strategy` | ≤12 heuristic tokens + `(heuristic fallback)` if vision unavailable | Yes |
| Support Case CSV | `support_cases_summary`, `total_cases`, `risk_signals`, `thematic_patterns`, `root_cause_samples`, `resolution_samples`, `recurring_failure_patterns` | Stub summary with row count if parse fails | Yes |

`CASE_SUMMARY_MAX_CASES` (env, default 25) caps theme/risk bullet output; excess items are summarized with a `(+N more ...)` suffix. The unified corpus prioritizes enriched fields before legacy `llm_analysis`.

### Support Case Sample Arrays
Support case ingestion now surfaces representative excerpts for downstream UI and analytics:

- `root_cause_samples`: Distinct trimmed root cause description excerpts (max 8, >20 chars, deduped by leading signature)
- `resolution_samples`: Distinct trimmed resolution/action excerpts (max 8)
- `recurring_failure_patterns`: List of `(pattern, count)` tuples derived from keyword classification (e.g., `configuration_error`, `performance_timeout`)

These arrays enable:
- Fast UI rendering of qualitative incident evidence without full CSV expansion
- Targeted reliability recommendation mapping (pattern → pillar deviation)
- Future ML clustering / trend visualization

If a CSV lacks the enriched columns (`msdfm_rootcausedescription`, `msdfm_resolution`), arrays will be present but empty to preserve schema stability.

## 🔄 Migration Notes

`llm_analysis` is **deprecated** and will be removed after the next minor release once the frontend consumes enrichment fields exclusively. Migrate to these sources:

- Diagrams: `raw_extracted_text`, `diagram_summary`, `analysis_metadata.structured_report`
- Support Cases: `support_cases_summary`, `risk_signals`, `thematic_patterns`, `total_cases`, `analysis_metadata.structured_report`
- Architecture: `raw_text`, `analysis_metadata.structured_report`

### Recommended Consumption Order
1. Explicit enrichment fields
2. `analysis_metadata.structured_report`
3. Legacy `llm_analysis` (only if above absent)

### Advantages
| Improvement | Impact |
|-------------|--------|
| Explicit separation | Easier UI rendering & caching |
| Deterministic fallbacks | Guarantees non-empty summaries offline/vision-fail |
| Structured transparency | Enables deeper analytics & provenance |
| Legacy isolation | Simplifies future removal of heuristic fields |

### Action Items
Refactor any client code referencing `llm_analysis` to prefer new enrichment fields. For full narrative context switch to `analysis_metadata.structured_report`.

