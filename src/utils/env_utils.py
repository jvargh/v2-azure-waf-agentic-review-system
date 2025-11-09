"""
Environment utilities for Azure Well-Architected Framework Agents.
Handles loading and validating environment variables for Azure AI services.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class EnvironmentConfig:
    """Configuration class for environment variables."""
    
    # Azure AI Foundry Configuration
    azure_ai_project_endpoint: Optional[str] = None
    azure_ai_model_deployment_name: Optional[str] = None
    
    # Azure OpenAI Configuration (fallback)
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    azure_openai_deployment_name: Optional[str] = None
    
    # Authentication
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    
    # Optional Configuration
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30
    
    @property
    def is_azure_ai_foundry_configured(self) -> bool:
        """Check if Azure AI Foundry is properly configured."""
        return bool(self.azure_ai_project_endpoint and self.azure_ai_model_deployment_name)
    
    @property
    def is_azure_openai_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured."""
        return bool(self.azure_openai_endpoint and 
                   (self.azure_openai_api_key or self.azure_client_id))


def load_env_vars(env_file_path: Optional[str] = None) -> EnvironmentConfig:
    """Load environment variables from a .env file (with fallback discovery) and system environment.

    Resolution order when ``env_file_path`` not provided:
      1. ``./.env`` in current working directory
      2. ``./azure-well-architected-agents/.env`` (repo nested path)
      3. ``../.env`` parent directory (useful when executing from a subfolder)
    The first existing file is loaded. This improves DX when running scripts from repo root or subpackages.
    """

    candidate_paths: List[Path] = []
    if env_file_path:
        candidate_paths.append(Path(env_file_path))
    else:
        cwd = Path.cwd()
        candidate_paths.extend([
            cwd / ".env",
            cwd / "azure-well-architected-agents" / ".env",
            cwd.parent / ".env",
        ])

    chosen: Optional[Path] = None
    for p in candidate_paths:
        try:
            if p.exists():
                chosen = p
                break
        except Exception:
            continue

    if chosen:
        logger.info(f"Loading environment variables from {chosen}")
        _load_dotenv_file(chosen)
    else:
        logger.info("No .env file found in candidate locations; relying on system environment variables only")
    
    # Create configuration from environment variables
    config = EnvironmentConfig(
        # Azure AI Foundry
        azure_ai_project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        azure_ai_model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
        
        # Azure OpenAI (fallback)
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
        
        # Authentication
        azure_client_id=os.getenv("AZURE_CLIENT_ID"),
        azure_client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        azure_tenant_id=os.getenv("AZURE_TENANT_ID"),
        
        # Optional
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30"))
    )
    
    logger.info(f"Environment configuration loaded. Azure AI Foundry: {config.is_azure_ai_foundry_configured}, "
                f"Azure OpenAI: {config.is_azure_openai_configured}")
    
    return config


def validate_env_vars(config: EnvironmentConfig, agent_type: str = "reliability") -> Dict[str, Any]:
    """
    Validate that mandatory environment variables are present.
    
    Args:
        config: EnvironmentConfig object to validate
        agent_type: Type of agent for specific validation requirements
        
    Returns:
        Dictionary with validation results and recommendations
        
    Raises:
        ValueError: If critical mandatory variables are missing
    """
    
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "recommendations": [],
        "configuration_type": None
    }
    
    # Check Azure AI Foundry configuration first (preferred)
    if config.is_azure_ai_foundry_configured:
        validation_result["configuration_type"] = "azure_ai_foundry"
        logger.info("Using Azure AI Foundry configuration")
        
        # Validate Azure AI Foundry specific requirements
        _validate_azure_ai_foundry(config, validation_result)
        
    elif config.is_azure_openai_configured:
        validation_result["configuration_type"] = "azure_openai"
        validation_result["warnings"].append("Using Azure OpenAI fallback configuration")
        logger.warning("Azure AI Foundry not configured, falling back to Azure OpenAI")
        
        # Validate Azure OpenAI specific requirements
        _validate_azure_openai(config, validation_result)
        
    else:
        validation_result["is_valid"] = False
        validation_result["errors"].append("Neither Azure AI Foundry nor Azure OpenAI are properly configured")
        validation_result["recommendations"].extend([
            "Set AZURE_AI_PROJECT_ENDPOINT and AZURE_AI_MODEL_DEPLOYMENT_NAME for Azure AI Foundry",
            "OR set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY for Azure OpenAI"
        ])
    
    # Agent-specific validation
    if agent_type == "reliability":
        _validate_reliability_agent(config, validation_result)
    
    # Authentication validation
    _validate_authentication(config, validation_result)
    
    # Log validation results
    if validation_result["errors"]:
        logger.error(f"Environment validation failed: {validation_result['errors']}")
        if validation_result["is_valid"]:
            raise ValueError(f"Critical environment variables missing: {validation_result['errors']}")
    
    if validation_result["warnings"]:
        logger.warning(f"Environment validation warnings: {validation_result['warnings']}")
    
    return validation_result


def _load_dotenv_file(env_path: Path) -> None:
    """Load environment variables from .env file."""
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
                else:
                    logger.warning(f"Invalid line format in .env file at line {line_num}: {line}")
                    
    except Exception as e:
        logger.error(f"Error loading .env file {env_path}: {e}")


def _validate_azure_ai_foundry(config: EnvironmentConfig, result: Dict[str, Any]) -> None:
    """Validate Azure AI Foundry specific configuration."""
    
    # Check endpoint format
    if config.azure_ai_project_endpoint:
        if not config.azure_ai_project_endpoint.startswith("https://"):
            result["errors"].append("AZURE_AI_PROJECT_ENDPOINT must start with https://")
        
        if "/api/projects/" not in config.azure_ai_project_endpoint:
            result["warnings"].append("AZURE_AI_PROJECT_ENDPOINT should contain '/api/projects/' path")
    
    # Check model deployment
    if not config.azure_ai_model_deployment_name:
        result["errors"].append("AZURE_AI_MODEL_DEPLOYMENT_NAME is required for Azure AI Foundry")
    
    # Recommendations
    result["recommendations"].extend([
        "Ensure your Azure AI Foundry project has the specified model deployed",
        "Verify you have appropriate RBAC permissions for the Azure AI project"
    ])


def _validate_azure_openai(config: EnvironmentConfig, result: Dict[str, Any]) -> None:
    """Validate Azure OpenAI specific configuration."""
    
    # Check endpoint format
    if config.azure_openai_endpoint:
        if not config.azure_openai_endpoint.startswith("https://"):
            result["errors"].append("AZURE_OPENAI_ENDPOINT must start with https://")
        
        if not config.azure_openai_endpoint.endswith(".openai.azure.com"):
            result["warnings"].append("AZURE_OPENAI_ENDPOINT should end with '.openai.azure.com'")
    
    # Check API version
    if config.azure_openai_api_version:
        valid_versions = ["2024-10-21", "2024-08-01-preview", "2024-06-01", "2024-05-01-preview"]
        if config.azure_openai_api_version not in valid_versions:
            result["warnings"].append(f"Azure OpenAI API version {config.azure_openai_api_version} may not be supported")
    
    # Authentication check
    if not config.azure_openai_api_key and not config.azure_client_id:
        result["errors"].append("Either AZURE_OPENAI_API_KEY or Azure service principal credentials required")


def _validate_reliability_agent(config: EnvironmentConfig, result: Dict[str, Any]) -> None:  # noqa: ARG001
    """Validate reliability agent specific requirements.

    config currently unused (kept for future extensibility and consistent signature).
    """
    
    # Check for MCP configuration (optional but recommended)
    mcp_enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"
    if not mcp_enabled:
        result["warnings"].append("MCP integration is disabled - real-time Azure documentation access unavailable")
    
    # Check for reliability-specific settings
    reliability_config = {
        "RELIABILITY_SCORING_WEIGHTS": os.getenv("RELIABILITY_SCORING_WEIGHTS"),
        "RELIABILITY_ASSESSMENT_MODE": os.getenv("RELIABILITY_ASSESSMENT_MODE", "comprehensive")
    }
    
    if reliability_config["RELIABILITY_ASSESSMENT_MODE"] not in ["basic", "comprehensive", "expert"]:
        result["warnings"].append("Unknown RELIABILITY_ASSESSMENT_MODE, using 'comprehensive' mode")


def _validate_authentication(config: EnvironmentConfig, result: Dict[str, Any]) -> None:
    """Validate authentication configuration."""
    
    has_api_key = bool(config.azure_openai_api_key)
    has_service_principal = bool(config.azure_client_id and config.azure_client_secret and config.azure_tenant_id)
    has_managed_identity = os.getenv("AZURE_USE_MANAGED_IDENTITY", "false").lower() == "true"
    
    auth_methods = sum([has_api_key, has_service_principal, has_managed_identity])
    
    if auth_methods == 0:
        result["warnings"].append("No explicit authentication configured - relying on DefaultAzureCredential")
        result["recommendations"].append("Consider configuring explicit authentication for production use")
    elif auth_methods > 1:
        result["warnings"].append("Multiple authentication methods configured - DefaultAzureCredential will choose precedence")


def get_sample_env_file() -> str:
    """
    Generate a sample .env file content with all supported variables.
    
    Returns:
        String content for a sample .env file
    """
    
    return """# Azure Well-Architected Framework Agents Environment Configuration

# ===== AZURE AI FOUNDRY CONFIGURATION (PREFERRED) =====
# Azure AI Foundry Project Endpoint - Get from Azure AI Foundry portal
AZURE_AI_PROJECT_ENDPOINT=https://your-project.services.ai.azure.com/api/projects/your-project-id
# Model deployment name in your Azure AI Foundry project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o-mini

# ===== AZURE OPENAI CONFIGURATION (FALLBACK) =====
# Azure OpenAI resource endpoint
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
# Azure OpenAI API key (if not using service principal)
AZURE_OPENAI_API_KEY=your-api-key-here
# Azure OpenAI API version
AZURE_OPENAI_API_VERSION=2024-10-21
# Azure OpenAI deployment name
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini

# ===== AZURE AUTHENTICATION =====
# Service Principal credentials (optional)
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id

# Use managed identity (for Azure-hosted applications)
AZURE_USE_MANAGED_IDENTITY=false

# ===== AGENT CONFIGURATION =====
# Logging level
LOG_LEVEL=INFO
# Maximum retry attempts
MAX_RETRIES=3
# Timeout in seconds
TIMEOUT_SECONDS=30

# ===== MCP CONFIGURATION =====
# Enable Model Context Protocol for real-time documentation access
MCP_ENABLED=true

# ===== RELIABILITY AGENT SPECIFIC =====
# Assessment mode: basic, comprehensive, expert
RELIABILITY_ASSESSMENT_MODE=comprehensive
# Custom scoring weights (JSON format)
RELIABILITY_SCORING_WEIGHTS={"high_availability": 0.25, "disaster_recovery": 0.25, "fault_tolerance": 0.20, "backup_restore": 0.15, "monitoring": 0.15}
"""


# Example usage and testing
if __name__ == "__main__":
    # Configure logging for testing
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("🔧 Environment Utilities Test")
    print("=" * 50)
    
    # Load configuration
    config = load_env_vars()
    
    # Validate configuration
    try:
        validation_result = validate_env_vars(config, "reliability")
        
        print(f"\n✅ Configuration Type: {validation_result['configuration_type']}")
        print(f"✅ Is Valid: {validation_result['is_valid']}")
        
        if validation_result["warnings"]:
            print("\n⚠️  Warnings:")
            for warning in validation_result["warnings"]:
                print(f"   - {warning}")
        
        if validation_result["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in validation_result["recommendations"]:
                print(f"   - {rec}")
                
    except ValueError as e:
        print(f"\n❌ Validation failed: {e}")
        # Generate sample .env file
        print("\n📄 Sample .env file content:")
        print(get_sample_env_file())