# Backend Error Handling & Logging

This document describes the error handling and logging strategy for the Azure Well-Architected Agents backend, helping developers maintain reliability and traceability.

---

## 1. Error Handling Strategy

- **Centralized Error Propagation**: Errors from agents and analysis modules are propagated to the orchestrator, which handles them uniformly.
- **Custom Exceptions**: Use custom exception classes for domain-specific errors (e.g., `AssessmentError`, `AgentError`).
- **API Error Responses**: API endpoints return structured error responses (HTTP status codes, error messages, details).
- **Validation**: Input data is validated early (artifact normalization) to prevent downstream errors.

---

## 2. Example Error Handling Code

```python
# orchestrator.py (simplified)
class Orchestrator:
    def run_assessment(self):
        results = {}
        for agent in self.agents:
            try:
                score, findings = agent.analyze()
                results[agent.__class__.__name__] = {
                    'score': score,
                    'findings': findings
                }
            except Exception as e:
                results[agent.__class__.__name__] = {
                    'error': str(e)
                }
        return results
```

---

## 3. Logging Configuration

- **Centralized Logging**: All modules use `logging_config.py` for consistent log formatting and output.
- **Log Levels**: Use appropriate log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- **Log Outputs**: Logs can be written to files, stdout, or external systems (e.g., Azure Monitor).

---

## 4. Example Logging Code

```python
# logging_config.py (simplified)
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
    )

# Usage in modules
import logging
logger = logging.getLogger(__name__)

logger.info('Assessment started')
logger.error('Agent failed', exc_info=True)
```

---

## 5. Recommendations

- Always log errors with stack traces for debugging.
- Use structured error responses in APIs.
- Validate inputs early and fail fast.

---

For configuration and environment management, see the config documentation.