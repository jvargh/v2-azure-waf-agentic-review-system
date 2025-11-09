# MongoDB Setup for Azure Well-Architected Reviews

## Database: `well_architected`

### Collections

#### 1. **assessments**
Main collection storing all assessment data.

**Indexes:**
- `id` (unique) - Primary identifier
- `created_at` - Timestamp sorting
- `status` - Query by status

**Schema:**
```json
{
  "id": "assess_1730840123",
  "name": "Production Architecture Review",
  "description": "Comprehensive review of production environment",
  "created_at": "2025-11-05T10:15:23.456Z",
  "status": "completed",
  "progress": 100,
  "current_phase": "Completed",
  "documents": [
    {
      "id": "doc_1",
      "filename": "architecture.txt",
      "content_type": "text/plain",
      "size": 5432,
      "category": "architecture",
      "uploaded_at": "2025-11-05T10:16:00.123Z",
      "raw_text": "Full architecture description...",
      "llm_analysis": "Architecture Analysis: architecture.txt\n\nIdentified Azure Services...",
      "analysis_metadata": {
        "components_identified": [
          {"service": "app service", "category": "compute"},
          {"service": "sql database", "category": "storage"}
        ],
        "pillar_signals": {
          "reliability": ["Multi-region deployment mentioned"],
          "security": ["Key vault for secrets"]
        },
        "architectural_patterns": ["Microservices", "Event-Driven"],
        "key_insights": [
          "Reliability: 3 relevant patterns detected",
          "Security: 2 relevant patterns detected"
        ]
      }
    }
  ],
  "unified_corpus": "=== ARCHITECTURE NARRATIVE ===\n## architecture.txt\nFull text...",
  "pillar_results": [
    {
      "pillar": "Reliability",
      "overall_score": 68,
      "subcategories": {
        "RE01: Define reliability targets": 70,
        "RE02: Use failure mode analysis": 65,
        "RE03: Identify and rate flows": 60
      },
      "recommendations": [
        {
          "pillar": "Reliability",
          "title": "Implement multi-region failover",
          "reasoning": "Single region deployment creates availability risk",
          "details": "Deploy to paired Azure regions with Traffic Manager",
          "priority": "High",
          "impact": "Significantly improves availability and disaster recovery",
          "effort": "Medium",
          "azure_service": "Azure Traffic Manager",
          "cross_pillar_considerations": [
            "⚠ Cost reduction measures may undermine availability targets - Prioritize cost optimization in non-critical paths"
          ]
        }
      ]
    }
  ],
  "cross_pillar_conflicts": [
    {
      "type": "cost_vs_reliability",
      "pillar_a": "Cost Optimization",
      "pillar_b": "Reliability",
      "description": "Cost reduction measures may undermine availability targets",
      "mitigation": "Prioritize cost optimization in non-critical paths; preserve redundancy for critical flows"
    }
  ],
  "overall_architecture_score": 64.2
}
```

**Status Values:**
- `pending` - Created, awaiting document upload
- `preprocessing` - Analyzing uploaded documents
- `analyzing` - Running pillar agents
- `aligning` - Performing cross-pillar alignment
- `completed` - Assessment finished successfully
- `failed` - Assessment encountered error

**Category Values (for documents):**
- `architecture` - Architecture description documents
- `case` - Support case CSV files
- `diagram` - Architecture diagrams/images

## Environment Variables

```bash
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017
MONGO_DB=well_architected

# Azure OpenAI (for agent execution)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Or Azure AI Foundry
AZURE_AI_PROJECT_CONNECTION_STRING=your-connection-string
```

## MongoDB Installation

### Windows (using MongoDB Community Edition):

1. **Download MongoDB:**
   ```powershell
   # Download from https://www.mongodb.com/try/download/community
   # Or using Chocolatey:
   choco install mongodb
   ```

2. **Start MongoDB:**
   ```powershell
   # Start as service (if installed as service)
   net start MongoDB
   
   # Or run directly
   mongod --dbpath C:\data\db
   ```

3. **Verify Connection:**
   ```powershell
   mongosh
   # In mongo shell:
   use well_architected
   db.assessments.find()
   ```

### Using Docker (Recommended):

```bash
# Run MongoDB container
docker run -d --name mongodb -p 27017:27017 -v mongodb_data:/data/db mongo:latest

# Verify
docker ps
```

## Python Dependencies

Install motor (async MongoDB driver):

```bash
pip install motor==3.3.1
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Database Operations

### Create Indexes (Automatic on Startup):

The FastAPI backend automatically creates indexes when it starts:

```python
await mongo_db["assessments"].create_index("id", unique=True)
await mongo_db["assessments"].create_index("created_at")
await mongo_db["assessments"].create_index("status")
```

### Query Examples:

```python
# Find all assessments
assessments = await mongo_db["assessments"].find({}).to_list(100)

# Find by status
completed = await mongo_db["assessments"].find({"status": "completed"}).to_list(100)

# Find by ID
assessment = await mongo_db["assessments"].find_one({"id": "assess_123"})

# Update progress
await mongo_db["assessments"].update_one(
    {"id": "assess_123"},
    {"$set": {"progress": 50, "current_phase": "Pillar Evaluation"}}
)
```

## Data Retention

**Recommendations:**
- Keep completed assessments for 90 days minimum
- Archive older assessments to separate collection
- Implement TTL index for automatic cleanup (optional)

```python
# TTL index for 90-day retention (optional)
await mongo_db["assessments"].create_index(
    "created_at",
    expireAfterSeconds=7776000  # 90 days
)
```

## Backup Strategy

```bash
# Daily backup
mongodump --db well_architected --out /backup/$(date +%Y%m%d)

# Restore
mongorestore --db well_architected /backup/20251105/well_architected
```

## Performance Tuning

**Recommended Settings:**

```javascript
// In mongo shell
use well_architected

// Check collection stats
db.assessments.stats()

// Compound index for common queries
db.assessments.createIndex({ "status": 1, "created_at": -1 })

// Index for document searches within assessments
db.assessments.createIndex({ "documents.category": 1 })
```

## Connection Pool Settings

In `server.py`, the connection is configured with:

```python
client = AsyncIOMotorClient(
    mongo_uri,
    serverSelectionTimeoutMS=1200,
    maxPoolSize=50,
    minPoolSize=10
)
```

## Monitoring Queries

```python
# Assessment count by status
db.assessments.aggregate([
  { $group: { _id: "$status", count: { $sum: 1 } } }
])

# Average progress by status
db.assessments.aggregate([
  { $group: { _id: "$status", avgProgress: { $avg: "$progress" } } }
])

# Top 10 recent assessments
db.assessments.find().sort({ created_at: -1 }).limit(10)
```

## Fallback Behavior

If MongoDB is unavailable, the backend automatically falls back to in-memory storage:

```python
ASSESSMENTS: Dict[str, Dict] = {}  # In-memory fallback
```

**Note:** In-memory storage is lost on server restart. MongoDB is required for production use.
