# Azure OpenAI Integration & Hybrid Scoring

## Overview

This document describes the unified Azure OpenAI provider architecture and the shadow hybrid scoring pathway introduced to centralize LLM/embedding operations and prepare for semantic scoring enhancements.

## Architecture

### Centralized Provider Pattern

The system now uses a centralized `LLMProvider` abstraction (`backend/app/services/llm_provider.py`) that:

- **Manages Azure OpenAI clients** (chat, embeddings, vision) via a single configuration surface
- **Implements operational resilience**: retry logic (4 attempts, linear backoff 0.75s), per-second token bucket rate limiting, concurrency semaphore (max 6 parallel requests)
- **Provides in-memory embedding cache** (SHA256-keyed) to avoid redundant API calls
- **Minimal structured logging** (JSON format with event, latency_ms, attempt, success/error fields)
- **Auto-selects deployment** (fast vs quality) based on estimated prompt token count (threshold: 600 tokens)

### Configuration

Settings are loaded via `backend/app/config/azure_openai.py` (`load_azure_openai_settings()`) from environment variables:

#### Core Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI resource endpoint (required) | - |
| `AZURE_OPENAI_API_KEY` | API key (or use managed identity) | - |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-10-21` |
| `AZURE_OPENAI_CHAT_FAST_DEPLOYMENT` | Fast chat model deployment name | `gpt-4o-mini` |
| `AZURE_OPENAI_CHAT_QUALITY_DEPLOYMENT` | Quality chat model deployment name | `gpt-4o` |
| `AZURE_OPENAI_EMBEDDING_DEPLOYMENT` | Embedding model deployment name | `text-embedding-3-small` |
| `AZURE_OPENAI_VISION_DEPLOYMENT` | Vision model deployment name | `gpt-4o-mini` |

#### Feature Flags

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_ENABLED` | Enable LLM chat operations | `true` |
| `EMBEDDINGS_ENABLED` | Enable embedding operations | `true` |
| `VISION_ENABLED` | Auto-enable vision analysis when diagrams present | `true` |
| `ENABLE_HYBRID_SHADOW` | Attach experimental hybrid scoring (non-intrusive) | `false` |

#### Operational Controls

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_OPENAI_MAX_CONCURRENT` | Max parallel requests (semaphore) | `6` |
| `AZURE_OPENAI_RATE_LIMIT_PER_SEC` | Token bucket refill rate (per second) | `8` |
| `AZURE_OPENAI_RETRY_ATTEMPTS` | Simple retry count | `4` |
| `AZURE_OPENAI_RETRY_BACKOFF` | Linear backoff base (seconds) | `0.75` |
| `AZURE_OPENAI_FAST_THRESHOLD_TOKENS` | Prompt token threshold for fast vs quality | `600` |

#### Managed Identity (Optional)

| Variable | Description | Default |
|----------|-------------|---------|
| `AZURE_USE_MANAGED_IDENTITY` | Use managed identity instead of API key | `false` |

## Fast vs Quality Heuristic

The provider auto-selects deployment based on estimated prompt token count:

- **< 600 tokens**: Use `AZURE_OPENAI_CHAT_FAST_DEPLOYMENT` (optimized for lower latency, cost-efficient)
- **≥ 600 tokens**: Use `AZURE_OPENAI_CHAT_QUALITY_DEPLOYMENT` (optimized for complex reasoning)

Override via `force_mode` parameter when calling `provider.chat()`.

## Retry & Rate Limiting

### Simple Retry

- **Attempts**: 4 (configurable via `AZURE_OPENAI_RETRY_ATTEMPTS`)
- **Backoff**: Linear (`0.75s * attempt_number`)
- **Strategy**: Retry all errors (no selective filtering by status code)
- **Logging**: Each attempt logged with latency, error details

### Token Bucket Rate Limiting

- **Refill Rate**: Per-second (configurable via `AZURE_OPENAI_RATE_LIMIT_PER_SEC`)
- **Capacity**: Equal to refill rate
- **Behavior**: Requests wait up to 1 second if bucket empty; prevents burst exceeding configured rate

### Concurrency Guard

- **Semaphore**: Max 6 parallel requests (configurable via `AZURE_OPENAI_MAX_CONCURRENT`)
- **Scope**: Applied across all LLM operations (chat, embeddings, vision)

## Embedding Cache

- **Strategy**: In-memory SHA256 hash → vector map
- **Scope**: Per provider instance (process-level)
- **Persistence**: None (cache cleared on restart)
- **Behavior**: Repeat embedding requests for identical text return cached vector without API call

## Logging Format

Minimal JSON logs emitted for each LLM operation:

```json
{
  "event": "chat|embed|vision",
  "attempt": 0,
  "latency_ms": 245,
  "success": true,
  "error": null,
  "mode": "auto|fast|quality",
  "deployment": "gpt-4o-mini",
  "prompt_tokens_estimate": 320
}
```

## Integration Points

### Server Initialization (`backend/server.py`)

```python
from backend.app.config.azure_openai import load_azure_openai_settings
from backend.app.services.llm_provider import LLMProvider

settings = load_azure_openai_settings()
openai_client = AsyncAzureOpenAI(...) if settings.api_key else None
llm_provider = LLMProvider(settings, openai_client)
```

### Document Analysis (`backend/app/analysis/document_analyzer.py`)

```python
analyzer = DocumentAnalyzer(llm_enabled=True, llm_provider=llm_provider)
```

### Orchestrator (`backend/app/analysis/orchestrator.py`)

```python
orchestrator = AssessmentOrchestrator(llm_provider)
```

Orchestrator uses provider for:
- Embedding-based pillar evidence inference (diagrams)
- Semantic recommendation deduplication

### Artifact Normalizer (`backend/app/analysis/artifact_normalizer.py`)

Embedding functions accept optional `llm_provider` parameter:

```python
consolidated_evidence = collect_and_infer_pillar_evidence(documents, analysis_results, llm_provider)
```

## Shadow Hybrid Scoring

### Overview

Experimental hybrid scoring attaches an `experimental_scores.hybrid_llm` field to `PillarResult` when `ENABLE_HYBRID_SHADOW=true`. This does **NOT** alter existing `overall_score`, `subcategories`, or `recommendations`.

### Purpose

- **Preparation** for future retrieval + LLM semantic scoring enhancements
- **Non-intrusive** observation of hybrid scoring outputs without affecting production results
- **Baseline comparison** to measure delta vs current conservative scoring

### Implementation

Located in `backend/app/scoring/hybrid_llm_scorer.py`:

```python
def run_hybrid_shadow(pillar: str, unified_corpus: str, pillar_evidence: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pillar": pillar,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "placeholder",
        "concept_hits": len(pillar_evidence.get(pillar, {}).get("excerpts", [])),
        "evidence_count": ...,
        "provisional": {"subcategory_scores": {}, "explanation": "..."},
        "llm_rationale": None,
        "notes": "Enable retrieval index to enrich this structure in future iterations."
    }
```

### Invocation

Shadow scoring runs in `_evaluate_pillar` (server.py) after conservative scoring completes:

```python
if llm_provider and llm_provider.settings.enable_hybrid_shadow:
    from backend.app.scoring.hybrid_llm_scorer import run_hybrid_shadow
    shadow_payload = run_hybrid_shadow(code, corpus, pillar_evidence)
    experimental_scores = {"hybrid_llm": shadow_payload}
    # Attach to PillarResult without modifying overall_score
```

### Current Status

- **Placeholder implementation**: Returns structured metadata and concept hit counts
- **No retrieval index**: Semantic ranking and LLM rationale alignment deferred
- **Future expansion**: Will integrate retrieval-augmented concept detection, LLM subcategory scoring, and calibration blending

## Future Enhancements

### Phase 1: Retrieval Index

- **Objective**: Build pillar-specific semantic index from Well-Architected Framework documentation
- **Scope**: Embed subcategory practice descriptions; retrieve top-K relevant chunks per pillar
- **Integration**: `scripts/build_retrieval_index.py` to pre-process docs; hybrid scorer queries index during shadow run

### Phase 2: LLM Semantic Alignment

- **Objective**: Use LLM to assess retrieved practice chunks against corpus evidence
- **Scope**: Replace keyword-based concept detection with semantic similarity scoring
- **Integration**: Hybrid scorer invokes `provider.chat()` with structured prompt referencing retrieved chunks + corpus excerpts

### Phase 3: Calibration & Blending

- **Objective**: Weighted blending of deterministic baseline + LLM semantic scores
- **Scope**: Tunable alpha parameter (e.g., 70% deterministic, 30% LLM); evaluation harness to measure precision/recall
- **Integration**: Shadow mode comparison metrics; gradual rollout via feature flag

### Phase 4: Production Rollout

- **Objective**: Replace conservative scoring with hybrid pipeline when calibration targets met
- **Scope**: Preserve transparency (maintain `scoring_breakdown` with hybrid adjustments)
- **Integration**: Remove "shadow" designation; hybrid scores become primary `overall_score`

## Migration & Backward Compatibility

### Legacy Fallbacks

- **DocumentAnalyzer**: If `llm_provider` not injected, falls back to inline `AsyncAzureOpenAI` client creation
- **Orchestrator embeddings**: Falls back to direct `OpenAI()` client if provider unavailable, then bag-of-words cosine
- **Artifact normalizer**: Same fallback chain (provider → OpenAI → bag-of-words)

### Existing Tests

- No breaking changes to existing test suite
- Tests that mock `AsyncAzureOpenAI` continue to work
- New tests (`test_azure_openai_config.py`, `test_hybrid_scoring_shadow.py`) added for provider and hybrid paths

## Troubleshooting

### Provider Initialization Failure

**Symptom**: Log line `[INIT] LLMProvider initialization failed: ...`

**Causes**:
- Missing `AZURE_OPENAI_ENDPOINT` or `AZURE_OPENAI_API_KEY`
- Invalid endpoint format (must start with `https://`)
- Config validation error (check `backend/app/config/azure_openai.py` error messages)

**Resolution**:
- Verify environment variables in `.env` file
- Ensure endpoint format: `https://<resource>.openai.azure.com`
- Check API key is not expired

### Embedding Cache Misses

**Symptom**: High API call volume for identical text

**Cause**: Cache key mismatch (SHA256 hash differs due to whitespace variations)

**Resolution**: Normalize text before embedding (strip, lowercase if appropriate)

### Rate Limiting Delays

**Symptom**: Requests taking longer than expected

**Cause**: Token bucket empty; requests waiting for refill

**Resolution**:
- Increase `AZURE_OPENAI_RATE_LIMIT_PER_SEC` if quota allows
- Reduce concurrent request load
- Monitor logs for `latency_ms` spikes

### Shadow Scoring Not Attaching

**Symptom**: `experimental_scores` field missing from `PillarResult`

**Causes**:
- `ENABLE_HYBRID_SHADOW` not set to `true`
- `llm_provider` is `None` (initialization failed)
- Exception during `run_hybrid_shadow` (check logs for `[hybrid-shadow] ... shadow scoring failed`)

**Resolution**:
- Set `ENABLE_HYBRID_SHADOW=true` in `.env`
- Fix provider initialization errors first
- Review stack trace if exception logged

## Performance Considerations

### Latency Budget

- **Chat (fast)**: ~200–500ms per request
- **Chat (quality)**: ~500–1500ms per request
- **Embeddings**: ~100–300ms per batch (up to 16 texts)
- **Vision**: ~800–2000ms per diagram analysis

### Cost Optimization

- **Use fast deployment** for short prompts (< 600 tokens)
- **Enable embedding cache** (in-memory; no additional cost)
- **Batch embeddings** when possible (orchestrator combines texts before calling provider)
- **Monitor token usage** via Azure portal; adjust concurrency/rate limits to stay within quota

### Concurrency Tuning

Default max concurrency: 6 parallel requests

- **Increase** if quota supports higher throughput and latency is acceptable
- **Decrease** if experiencing throttling (429 errors) or quota exhaustion

## Security Considerations

### API Key Management

- **Never commit** `.env` file to version control
- Use **Azure Key Vault** or managed identity in production
- Rotate keys periodically

### Managed Identity (Recommended for Azure-hosted apps)

Set `AZURE_USE_MANAGED_IDENTITY=true` and omit `AZURE_OPENAI_API_KEY`. Ensure app has appropriate RBAC role on Azure OpenAI resource (e.g., `Cognitive Services User`).

### Data Privacy

- Embedding cache is **in-memory only** (not persisted)
- No user data logged in provider logs (only metadata: latency, attempt, error type)
- Review corpus content for PII before assessment submission

## References

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/azure/well-architected/)
- [Retrieval-Augmented Generation (RAG) Patterns](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [Token Bucket Rate Limiting](https://en.wikipedia.org/wiki/Token_bucket)
