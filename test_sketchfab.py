import httpx
import asyncio

SKETCHFAB_API_TOKEN = "e2612b2d45d44426b56ea86c2c75586d"

async def test_sketchfab():
    query = "heart"
    print(f"🔍 Testing Sketchfab search for: {query}...")
    url = "https://api.sketchfab.com/v3/search"
    params = {
        "q": query,
        "type": "models",
        "count": 1,
        "license": "by",
    }
    headers = {"Authorization": f"Token {SKETCHFAB_API_TOKEN}"}
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            print(f"Status Code: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                if data.get("results"):
                    uid = data["results"][0]["uid"]
                    print(f"✅ SUCCESS! Sketchfab Match Found: {uid}")
                else:
                    print("❌ No results found on Sketchfab.")
            else:
                print(f"❌ Error Detail: {resp.text}")
        except Exception as e:
            print(f"⚠️ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_sketchfab())
