import httpx
import asyncio

async def verify_api():
    url = "http://127.0.0.1:8000/generate"
    payload = {"prompt": "أذن"}
    print(f"🚀 Testing /generate with: {payload['prompt']}...")
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=25)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print("✅ API Response received:")
                print(f"   Name: {data.get('name')}")
                print(f"   Sketchfab ID: {data.get('sketchfab_id')}")
                print(f"   Model URL: {data.get('model_url')}")
                if data.get("sketchfab_id"):
                    print("🎉 SUCCESS! Sketchfab model resolved.")
                else:
                    print("⚠️ No Sketchfab ID found.")
            else:
                print(f"❌ Error: {resp.text}")
        except Exception as e:
            print(f"⚠️ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(verify_api())
