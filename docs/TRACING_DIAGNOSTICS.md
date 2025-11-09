# Azure AI Foundry Tracing Diagnostics

## Issue Identified
Tracing logs were not reaching AI Foundry due to silent failures in observability setup.

## Root Causes Fixed

### 1. Silent Observability Failures
**Problem**: `setup_azure_ai_observability()` errors were only logged at DEBUG level, making failures invisible to users.

**Fixed in**:
- `src/app/agents/pillar_agent_base.py` (line 119-122)
- `src/app/tools/mcp_tools.py` (line 150-153)

**Changes**:
- Changed log level from `DEBUG` to `WARNING`
- Added success confirmation at `INFO` level
- Added actionable guidance in error messages

### 2. Missing Application Insights Connection
**Common Issue**: AI Foundry project may not have Application Insights connected.

## How to Verify Tracing is Working

### Step 1: Run an Agent and Check for Warnings
```powershell
python -m src.app.agents.reliability_agent my_arch.txt
```

**Look for these log messages**:

✅ **Success** - You should see:
```
INFO - src.app.agents.pillar_agent_base - Azure AI Foundry observability configured successfully
```

❌ **Failure** - You'll see a WARNING:
```
WARNING - src.app.agents.pillar_agent_base - Failed to configure Azure AI observability (tracing will not be available): <error details>. Ensure Application Insights is connected to your AI Foundry project.
```

### Step 2: Check Environment Configuration
```powershell
# Verify your .env has the correct endpoint
cat .env | Select-String "AZURE_AI_PROJECT_ENDPOINT"
```

Expected format:
```
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project-id
```

### Step 3: Verify Application Insights in AI Foundry

1. Go to [Azure AI Foundry portal](https://ai.azure.com)
2. Navigate to your project
3. Go to **Settings** → **Properties**
4. Check if **Application Insights** is listed
5. If not connected:
   - Click **Connect Application Insights**
   - Select or create an Application Insights resource
   - Save changes

### Step 4: Check Azure Permissions

Ensure your Azure CLI credential has these roles on the AI Foundry project:
- `Azure AI Developer` or `Contributor`
- `Application Insights Component Contributor` (if connecting App Insights)

Verify current login:
```powershell
az account show
```

## Common Issues and Solutions

### Issue 1: "Application Insights resource not found"
**Solution**: Connect Application Insights to your AI Foundry project (see Step 3 above)

### Issue 2: "Authentication failed"
**Solutions**:
- Run `az login` and select the correct subscription
- Verify subscription: `az account show`
- Check if you have access: `az role assignment list --assignee $(az ad signed-in-user show --query id -o tsv) --all`

### Issue 3: "Project endpoint is invalid"
**Solution**: Verify the endpoint format in `.env`:
- Must start with `https://`
- Should contain `/api/projects/`
- Example: `https://eastus.api.azureml.ms/api/projects/12345678-1234-1234-1234-123456789abc`

### Issue 4: Still no traces in AI Foundry
**Troubleshooting**:
1. Check Application Insights directly in Azure Portal
2. Look for traces in Application Insights → Transaction search
3. Verify the instrumentation key matches
4. Check if there's a delay (traces can take 1-2 minutes to appear)
5. Verify network connectivity to Application Insights endpoint

## Testing Observability

### Quick Test Script
```python
import asyncio
import logging
from backend.app.agents.reliability_agent import ReliabilityAgent

# Enable INFO logging to see observability messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

async def test_tracing():
    agent = ReliabilityAgent()
    simple_arch = "Basic web app on Azure App Service with SQL Database"
    assessment = await agent.assess_architecture(simple_arch)
    print(f"Assessment completed. Score: {assessment.overall_score}")

if __name__ == "__main__":
    asyncio.run(test_tracing())
```

Save as `test_tracing.py` and run:
```powershell
python test_tracing.py
```

### Expected Output (Success)
```
INFO - src.utils.env_utils - Loading environment variables from C:\_Projects\MAF\wara\azure-well-architected-agents\.env
INFO - src.app.agents.pillar_agent_base - Azure AI Foundry observability configured successfully
INFO - src.app.agents.pillar_agent_base - ReliabilityAgent initialized (config: azure_ai_foundry)
Assessment completed. Score: 75
```

### Expected Output (Failure - needs attention)
```
INFO - src.utils.env_utils - Loading environment variables from C:\_Projects\MAF\wara\azure-well-architected-agents\.env
WARNING - src.app.agents.pillar_agent_base - Failed to configure Azure AI observability (tracing will not be available): Application Insights not connected. Ensure Application Insights is connected to your AI Foundry project.
INFO - src.app.agents.pillar_agent_base - ReliabilityAgent initialized (config: azure_ai_foundry)
Assessment completed. Score: 75
```

## Viewing Traces in AI Foundry

Once observability is working:

1. Go to [Azure AI Foundry portal](https://ai.azure.com)
2. Open your project
3. Navigate to **Tracing** or **Monitoring**
4. You should see:
   - Agent execution traces
   - LLM calls with prompts and responses
   - Token usage
   - Latency metrics
   - Error traces (if any)

## Additional Resources

- [Azure AI Foundry Tracing Documentation](https://learn.microsoft.com/azure/ai-studio/how-to/develop/trace-your-code)
- [Application Insights Overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
- [Azure AI Agent Framework Observability](https://learn.microsoft.com/azure/ai-studio/how-to/develop/agent-observability)

## Changes Made

### File: `src/app/agents/pillar_agent_base.py`
```python
# Before (line 119-122):
try:
    await client.setup_azure_ai_observability()
except Exception as obs_err:
    logger.debug("Failed to configure Azure AI observability: %s", obs_err)

# After:
try:
    await client.setup_azure_ai_observability()
    logger.info("Azure AI Foundry observability configured successfully")
except Exception as obs_err:
    logger.warning(
        "Failed to configure Azure AI observability (tracing will not be available): %s. "
        "Ensure Application Insights is connected to your AI Foundry project.",
        obs_err
    )
```

### File: `src/app/tools/mcp_tools.py`
```python
# Before (line 150-153):
try:
    await chat_client.setup_azure_ai_observability()
except Exception as obs_err:
    logger.debug(f"Observability setup skipped: {obs_err}")

# After:
try:
    await chat_client.setup_azure_ai_observability()
    logger.info("MCP client observability configured successfully")
except Exception as obs_err:
    logger.warning(
        "Failed to configure MCP observability (tracing will not be available): %s. "
        "Ensure Application Insights is connected to your AI Foundry project.",
        obs_err
    )
```

## Next Steps

1. ✅ Run an agent to check for the new WARNING/INFO messages
2. ✅ If you see a warning, connect Application Insights to your AI Foundry project
3. ✅ Verify traces appear in AI Foundry portal within 1-2 minutes
4. ✅ If traces still don't appear, check Application Insights directly in Azure Portal
