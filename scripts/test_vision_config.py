"""Quick test to verify Azure OpenAI vision configuration."""
import sys
import os
sys.path.insert(0, str(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from backend.app.config.azure_openai import load_azure_openai_settings

def main():
    print("=== Azure OpenAI Vision Configuration Test ===\n")
    
    settings = load_azure_openai_settings()
    
    print(f"Endpoint: {settings.endpoint}")
    print(f"API Version: {settings.api_version}")
    print(f"API Key: {'SET' if settings.api_key else 'NOT SET'}")
    print()
    print(f"Chat Fast Deployment: {settings.chat_fast_deployment}")
    print(f"Chat Quality Deployment: {settings.chat_quality_deployment}")
    print(f"Embedding Deployment: {settings.embedding_deployment}")
    print(f"Vision Deployment: {settings.vision_deployment}")
    print()
    print(f"LLM Enabled: {settings.llm_enabled}")
    print(f"Embeddings Enabled: {settings.embeddings_enabled}")
    print(f"Vision Enabled: {settings.vision_enabled}")
    print(f"Hybrid Shadow Enabled: {settings.enable_hybrid_shadow}")
    print()
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT', 'NOT SET')}")
    print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'NOT SET')}")
    print(f"  AZURE_OPENAI_VISION_DEPLOYMENT: {os.getenv('AZURE_OPENAI_VISION_DEPLOYMENT', 'NOT SET')}")
    print(f"  VISION_ENABLED: {os.getenv('VISION_ENABLED', 'NOT SET (defaults to True)')}")
    print()
    
    # Diagnosis
    print("=== Diagnosis ===")
    if not settings.vision_enabled:
        print("❌ Vision is DISABLED via VISION_ENABLED environment variable")
    elif not settings.vision_deployment:
        print("⚠️  Vision deployment not configured (will use chat_quality_deployment as fallback)")
    else:
        print("✓ Vision configuration looks good")
    
    if settings.vision_deployment == "gpt-4.1":
        print("⚠️  WARNING: gpt-4.1 may not support vision API")
        print("   Consider using gpt-4o, gpt-4o-mini, or gpt-4-vision-preview")

if __name__ == "__main__":
    main()
