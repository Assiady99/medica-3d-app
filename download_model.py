import urllib.request
import os

model_dir = "models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

url = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Box/Glb/Box.glb"
output = os.path.join(model_dir, "test_box.glb")

try:
    print(f"Downloading {url}...")
    urllib.request.urlretrieve(url, output)
    print(f"Success! Saved to {output}")
except Exception as e:
    print(f"Failed to download: {e}")
