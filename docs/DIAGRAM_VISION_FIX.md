# Diagram Vision Analysis Fix

## Problem
After the Azure OpenAI refactor, diagram analysis was returning empty/generic content instead of detailed vision-based analysis.

## Root Cause
1. **Before refactor**: `DocumentAnalyzer` created its own `azure_client` using environment variables directly
2. **After refactor**: `DocumentAnalyzer` receives an `llm_provider` that tries to use `AZURE_OPENAI_VISION_DEPLOYMENT`
3. **Issue**: The vision deployment (`gpt-4o-mini` by default) didn't exist in the user's Azure OpenAI resource
4. **Result**: Vision API returned 404 error silently, causing empty diagram analysis

## Solution
1. **Added `.env` configuration**: `AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4.1` to use existing deployment
2. **Enhanced error handling**: Added comprehensive debug logging to trace vision execution
3. **Improved fallback logic**: Enhanced structured report to use vision content when available, intelligent heuristics otherwise
4. **Better result handling**: Support both dict and object responses from vision API

## Changes Made

### Configuration (`.env`)
```bash
# Vision API Configuration
AZURE_OPENAI_VISION_DEPLOYMENT=gpt-4.1
```

### Code Changes
1. **`document_analyzer.py` line 300-340**: Added debug logging for vision execution path
   - Shows vision_enabled status
   - Shows deployment being used
   - Logs result type and keys
   - Reports errors clearly
   - Tracks vision_summary population

2. **`document_analyzer.py` line 331-338**: Enhanced result handling
   - Support dict response with `result['choices'][0]['message']['content']`
   - Support object response with `result.choices[0].message.content`
   - Better error message extraction (truncated to 100 chars)

3. **`document_analyzer.py` line 1060-1117**: Enhanced structured report generation
   - Added `vision_summary` parameter to `_compose_structured_diagram_report()`
   - Prioritize vision analysis when available (50+ chars)
   - Use intelligent heuristic fallback when vision unavailable
   - Conditional execution summary building based on vision availability

### Testing Tools
1. **`scripts/test_vision_config.py`**: Validates vision configuration
2. **`scripts/test_vision_api.py`**: Tests actual vision API call with test image

## Verification

### Test Vision Configuration
```bash
python scripts/test_vision_config.py
```
Expected output:
- Vision Enabled: True
- Vision Deployment: gpt-4.1
- ✓ Vision configuration looks good

### Test Vision API
```bash
python scripts/test_vision_api.py
```
Expected output:
- ✓ Vision API call succeeded!
- Response showing image description

### Run Unit Tests
```bash
python -m pytest tests/test_diagram_vision_path.py -v
```
Expected: 4 tests passing

## Debug Output
When uploading a diagram, you'll now see debug output in the backend logs:
```
[DIAGRAM] llm_provider available, vision_enabled=True, vision_deployment=gpt-4.1
[DIAGRAM] Calling llm_provider.vision() with 12345 base64 chars
[DIAGRAM] Vision result type: <class 'dict'>, keys: dict_keys(['model', 'choices', 'usage'])
[DIAGRAM] Vision summary extracted: 345 chars
[DIAGRAM] vision_summary=SET, extracted_text=150 chars, summary_source=345 chars
[DIAGRAM] structured_report executive_summary preview: Architecture diagram analysis...
```

## Deployment Requirements

### Supported Vision Models
Your Azure OpenAI deployment must support vision API. Compatible models:
- `gpt-4o` (recommended - best quality)
- `gpt-4o-mini` (recommended - cost-effective)
- `gpt-4-vision-preview` (older generation)
- `gpt-4.1` (if it includes vision capabilities)

### Verify Model Support
Check your Azure OpenAI resource in Azure Portal:
1. Navigate to your resource: `azurefoundryjv01.cognitiveservices.azure.com`
2. Go to "Model deployments"
3. Verify the deployed model supports vision (check model documentation)
4. Update `.env` with the correct deployment name

## Future Improvements
1. Add retry logic for transient vision API failures
2. Cache vision analysis results by image hash
3. Add fallback to local OCR when vision API unavailable
4. Implement progressive enhancement (basic → vision → enhanced)
5. Add vision analysis quality scoring
