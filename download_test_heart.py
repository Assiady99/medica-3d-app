import httpx
import os

# Professional heart model from Code for FUKUI (Institutional medical asset)
HEART_URL = "https://code4fukui.github.io/human_organs/heart.glb"

def download_heart():
    print(f"📥 Attempting to download professional heart model...")
    try:
        # Using a browser-like user agent to avoid basic blocks
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        with httpx.Client(follow_redirects=True, timeout=60, headers=headers) as client:
            resp = client.get(HEART_URL)
            resp.raise_for_status()
            
            os.makedirs("models", exist_ok=True)
            with open("models/heart_pro.glb", "wb") as f:
                f.write(resp.content)
            print(f"✅ Success! Professional heart saved as 'models/heart_pro.glb' ({len(resp.content)} bytes)")
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    download_heart()
