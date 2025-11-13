# Backend Configuration & Environment Management

This document explains how configuration and environment management are handled in the Azure Well-Architected Agents backend, ensuring secure and flexible deployments.

---

## 1. Configuration Files & Modules

- **env_utils.py**: Manages environment variables and configuration loading.
- **azure_openai.py**: Handles Azure OpenAI credentials and settings.
- **pillar JSON files**: Store scoring criteria and thresholds for each pillar.

---

## 2. Environment Variables

- Sensitive information (API keys, secrets) is stored in environment variables.
- Use `.env` files (with python-dotenv) for local development.
- Example variables:
  - `AZURE_OPENAI_KEY`
  - `DATABASE_URL`
  - `LOG_LEVEL`

---

## 3. Example Usage

```python
# env_utils.py (simplified)
import os

def get_env_variable(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        raise EnvironmentError(f"Missing required env var: {name}")
    return value

# Usage in modules
openai_key = get_env_variable('AZURE_OPENAI_KEY')
```

---

## 4. Configuration Best Practices

- Never hardcode secrets in code.
- Use environment variables for all sensitive and environment-specific settings.
- Document required variables in README or setup guides.
- Validate configuration at startup and fail fast if missing.

---

For diagrams and workflow, see the diagrams documentation.