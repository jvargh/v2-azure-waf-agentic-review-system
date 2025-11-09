"""Test that vision message content is properly accessible."""
import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, str(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))))

from backend.app.config.azure_openai import load_azure_openai_settings
from backend.app.services.llm_provider import LLMProvider
from openai import AsyncAzureOpenAI

async def test():
    settings = load_azure_openai_settings()
    client = AsyncAzureOpenAI(
        azure_endpoint=settings.endpoint,
        api_key=settings.api_key,
        api_version=settings.api_version
    )
    provider = LLMProvider(settings, client)
    
    # Test with 1x1 red pixel PNG
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=="
    
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "What color is this?"},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{test_image_b64}"}}
        ]}
    ]
    
    result = await provider.vision(messages)
    
    print(f"Result type: {type(result)}")
    print(f"Result keys: {result.keys()}")
    print(f"Choices: {len(result['choices'])}")
    print(f"Message type: {type(result['choices'][0]['message'])}")
    print(f"Message keys: {result['choices'][0]['message'].keys()}")
    print(f"Content accessible: {result['choices'][0]['message']['content'][:100]}")
    print("\n✅ Message content is properly accessible as dict!")

if __name__ == "__main__":
    asyncio.run(test())
