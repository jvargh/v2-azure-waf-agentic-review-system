"""(Relocated) End-to-End API Persistence Test"""
import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_api_persistence():
    async with httpx.AsyncClient(timeout=30.0) as client:
        create_payload = {
            "name": f"API Test Assessment {datetime.now().strftime('%H:%M:%S')}",
            "description": "Testing MongoDB persistence through API"
        }
        r = await client.post(f"{BASE_URL}/api/assessments", json=create_payload)
        r.raise_for_status()
        assessment_id = r.json()["id"]
        # list
        r2 = await client.get(f"{BASE_URL}/api/assessments")
        r2.raise_for_status()
        assert any(a["id"] == assessment_id for a in r2.json())

async def main():  # pragma: no cover
    await test_api_persistence()
    print("✅ API persistence basic cycle passed")

if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
