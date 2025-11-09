# Agent Prompts

This folder contains the system prompts and instructions for each Azure Well-Architected Framework agent.

## Files

- `reliability_agent_instructions.txt` - System instructions for the Reliability Agent

## Usage

Agents automatically load their instructions from these files at initialization. The instructions define:

- Agent role and expertise area
- Analysis requirements and focus areas  
- Expected output format and structure
- Scoring criteria and scales

## Adding New Agent Prompts

1. Create a new `.txt` file named `{agent_name}_instructions.txt`
2. Follow the existing format with clear sections for:
   - Role definition
   - Analysis requirements
   - Response format
   - Focus areas
3. Update the corresponding agent to load from this file

## Best Practices

- Keep instructions clear and specific
- Define expected JSON response formats explicitly
- Include scoring scales and criteria
- Reference Azure Well-Architected Framework principles
- Use structured sections for readability
- Maintain consistency across agent prompts

## Deprecation Notice

The legacy directory `src/prompts/` (with `reliability_prompts.py`) has been removed as it was unused. All prompt-related assets should now reside exclusively in this `src/app/prompts` directory. If programmatic prompt composition is required in the future, create a new module here (e.g., `prompt_builder.py`) rather than reintroducing the deprecated path.

Change Log:
- 2025-11-02: Removed unused `src/prompts/reliability_prompts.py` and documented consolidation.