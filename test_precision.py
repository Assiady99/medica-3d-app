import httpx
import asyncio

async def test_precision():
    url = "http://127.0.0.1:8000/generate"
    
    test_cases = [
        {"prompt": "محرك سيارة", "expected_contains": ["engine"]},
        {"prompt": "car engine", "expected_contains": ["engine"]},
        {"prompt": "قلب", "expected_contains": ["heart"]}
    ]
    
    print("🚀 Starting Precision Quality Test...")
    
    async with httpx.AsyncClient() as client:
        for case in test_cases:
            prompt = case["prompt"]
            print(f"\n🔍 Testing prompt: '{prompt}'...")
            try:
                resp = await client.post(url, json={"prompt": prompt}, timeout=25)
                if resp.status_code == 200:
                    data = resp.json()
                    name = data.get("name", "")
                    uid = data.get("sketchfab_id", "")
                    print(f"✅ Received: '{name}' (UID: {uid})")
                    
                    if uid == "5454444654c84c87bf84d1d9b1fc24eb" or "engine" in name.lower():
                        print("✨ PASS: Correct clinical/mechanical model found.")
                    else:
                        print("❌ FAIL: Irrelevant model returned.")
                else:
                    print(f"❌ API Error: {resp.status_code}")
            except Exception as e:
                print(f"⚠️ Connection Error: {e} (Is the server running?)")

if __name__ == "__main__":
    asyncio.run(test_precision())
