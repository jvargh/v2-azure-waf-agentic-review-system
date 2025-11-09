# Migrated from src.utils.env_utils with import path adjustments
from __future__ import annotations
import os, logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
logger = logging.getLogger(__name__)
@dataclass
class EnvironmentConfig:
    azure_ai_project_endpoint: Optional[str] = None
    azure_ai_model_deployment_name: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_api_version: Optional[str] = None
    azure_openai_deployment_name: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_tenant_id: Optional[str] = None
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30
    @property
    def is_azure_ai_foundry_configured(self) -> bool:
        return bool(self.azure_ai_project_endpoint and self.azure_ai_model_deployment_name)
    @property
    def is_azure_openai_configured(self) -> bool:
        return bool(self.azure_openai_endpoint and (self.azure_openai_api_key or self.azure_client_id))

def load_env_vars(env_file_path: Optional[str] = None) -> EnvironmentConfig:
    candidate_paths: List[Path] = []
    if env_file_path:
        candidate_paths.append(Path(env_file_path))
    else:
        cwd = Path.cwd()
        candidate_paths.extend([cwd/".env", cwd/"azure-well-architected-agents"/".env", cwd.parent/".env"])
    chosen: Optional[Path] = None
    for p in candidate_paths:
        try:
            if p.exists():
                chosen = p; break
        except Exception:
            continue
    if chosen:
        logger.info(f"Loading environment variables from {chosen}")
        _load_dotenv_file(chosen)
    config = EnvironmentConfig(
        azure_ai_project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT"),
        azure_ai_model_deployment_name=os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o-mini"),
        azure_openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_openai_deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
        azure_client_id=os.getenv("AZURE_CLIENT_ID"),
        azure_client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        azure_tenant_id=os.getenv("AZURE_TENANT_ID"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        timeout_seconds=int(os.getenv("TIMEOUT_SECONDS", "30")),
    )
    return config

def validate_env_vars(config: EnvironmentConfig, agent_type: str = "reliability") -> Dict[str, Any]:
    result = {"is_valid": True, "errors": [], "warnings": [], "recommendations": [], "configuration_type": None}
    if config.is_azure_ai_foundry_configured:
        result["configuration_type"] = "azure_ai_foundry"
    elif config.is_azure_openai_configured:
        result["configuration_type"] = "azure_openai"
        result["warnings"].append("Using Azure OpenAI fallback configuration")
    else:
        result["is_valid"] = False
        result["errors"].append("Neither Azure AI Foundry nor Azure OpenAI are properly configured")
    return result

def _load_dotenv_file(env_path: Path) -> None:
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line=line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    k,v=line.split('=',1); k=k.strip(); v=v.strip().strip('"').strip("'")
                    if k not in os.environ: os.environ[k]=v
    except Exception as e:
        logger.error(f"Error loading .env file {env_path}: {e}")
__all__ = ["EnvironmentConfig","load_env_vars","validate_env_vars"]
