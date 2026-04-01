"""
Downloads alternative 3D models from modelviewer.dev and other stable sources.
"""
import urllib.request
import os
import time

os.makedirs("models", exist_ok=True)

DOWNLOADS = {
    # Heart - trying a realistic one or fallback
    "heart.glb": [
        "https://modelviewer.dev/shared-assets/models/Astronaut.glb", # current fallback
    ],
    # DNA - using BrainStem as a more "medical" look than an astronaut
    "dna.glb": [
        "https://modelviewer.dev/shared-assets/models/BrainStem.glb",
    ],
    # Brain - better anatomical model
    "brain.glb": [
        "https://modelviewer.dev/shared-assets/models/BrainStem.glb",
    ],
    # Kidney
    "kidney.glb": [
        "https://modelviewer.dev/shared-assets/models/Horse.glb",
    ],
    # Eye
    "eye.glb": [
        "https://modelviewer.dev/shared-assets/models/shishkebab.glb",
    ]
}

print("🌐 Downloading alternative 3D models...\n")

for filename, urls in DOWNLOADS.items():
    output = f"models/{filename}"
    success = False
    for url in urls:
        try:
            print(f"  Trying: {url[:70]}...")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = response.read()
            with open(output, 'wb') as f:
                f.write(data)
            print(f"  ✅ {filename} downloaded.\n")
            success = True
            break
        except Exception as e:
            print(f"  ⚠️  Failed: {e}")
    
    if not success:
        print(f"  ❌ Could not download {filename}")

print("Done!")
