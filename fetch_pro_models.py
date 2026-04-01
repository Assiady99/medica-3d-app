import httpx
import os
import asyncio

MODELS = {
    "bee.glb": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/Bee/glTF-Binary/Bee.glb",
    "astronaut.glb": "https://modelviewer.dev/shared-assets/models/Astronaut.glb",
    "robot.glb": "https://modelviewer.dev/shared-assets/models/RobotExpressive.glb",
    "engine.glb": "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Assets/main/Models/2CylinderEngine/glTF-Binary/2CylinderEngine.glb",
}

async def download_file(name, url, client):
    print(f"📥 Downloading {name}...")
    try:
        resp = await client.get(url, timeout=60, follow_redirects=True)
        resp.raise_for_status()
        with open(f"models/{name}", "wb") as f:
            f.write(resp.content)
        print(f"✅ Saved {name}")
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

async def main():
    os.makedirs("models", exist_ok=True)
    async with httpx.AsyncClient() as client:
        tasks = [download_file(n, u, client) for n, u in MODELS.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
