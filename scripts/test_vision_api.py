"""Test if the configured vision deployment exists and supports vision."""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from backend.app.config.azure_openai import load_azure_openai_settings
from backend.app.services.llm_provider import LLMProvider
from openai import AsyncAzureOpenAI

async def test_vision():
    print("=== Testing Azure OpenAI Vision Configuration ===\n")
    
    settings = load_azure_openai_settings()
    
    print(f"Vision Enabled: {settings.vision_enabled}")
    print(f"Vision Deployment: {settings.vision_deployment}")
    print(f"Chat Quality Deployment (fallback): {settings.chat_quality_deployment}")
    print()
    
    if not settings.vision_enabled:
        print("❌ Vision is disabled. Set VISION_ENABLED=true in .env")
        return
    
    # Create client
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.endpoint,
        api_key=settings.api_key,
        api_version=settings.api_version
    )
    
    provider = LLMProvider(settings, client)
    
    # Test with a simple base64 1x1 red pixel PNG
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    
    messages = [
        {"role": "system", "content": "You describe images."},
        {"role": "user", "content": [
            {"type": "text", "text": "What color is this image?"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{test_image_b64}"}}
        ]}
    ]
    
    print("Testing vision API call...")
    try:
        result = await provider.vision(messages)
        
        if isinstance(result, dict):
            if result.get("disabled"):
                print("❌ Vision returned 'disabled'")
            elif result.get("error"):
                print(f"❌ Vision returned error: {result.get('error')}")
            else:
                print(f"✓ Vision API call succeeded!")
                print(f"Result type: {type(result)}")
                if hasattr(result, 'choices'):
                    content = result.choices[0].message.content
                    print(f"Response: {content[:200]}")
                else:
                    print(f"Result keys: {result.keys()}")
        else:
            print(f"✓ Vision API returned: {type(result)}")
            if hasattr(result, 'choices'):
                print(f"Response: {result.choices[0].message.content[:200]}")
                
    except Exception as e:
        print(f"❌ Exception calling vision API: {e.__class__.__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_vision())
