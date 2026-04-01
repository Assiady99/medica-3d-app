import base64
import os

# A minimal GLB file representing a simple red cube
# This is a base64 encoded version of a valid minimal GLB
glb_base64 = (
    "Z2xURgIAAADoAAAgkwEAAEpTT04eyIxhc3NldCI6eyJ2ZXJzaW9uIjoiMi4wIn0sInNjZW5lcyI6W3sib"
    "m9kZXMiOlswXX1dLCJub2RlcyI6W3sibWVzaCI6MH1dLCJtZXNoZXMiOlt7InByaW1pdGl2ZXMiOlt7ImF"
    "0dHJpYnV0ZXMiOnsiUE9TSVRJT04iOjF9LCJpbmRpY2VzIjoyLCJtYXRlcmlhbCI6MH1dfV0sImFjY2Vzc"
    "29ycyI6W3siY29tcG9uZW50VHlwZSI6NTEyNiwiY291bnQiOjgsInR5cGUiOiJWRUMzIiwiYnVmZmVyVml"
    "ldyI6MCwibWF4IjpbMC41LDAuNSwwLjVdLCJtaW4iOlt-MC41LC0wLjUsLTAuNV19LHsiY29tcG9uZW50V"
    "HlwZSI6NTEyNiwiY291bnQiOjgsInR5cGUiOiJWRUMzIiwiYnVmZmVyVmlldyI6MH0seyJjb21wb25lbnR"
    "UeXBlIjo1MTIzLCJjb3VudCI6MzYsInR5cGUiOiJTQ0FMQVIiLCJidWZmZXJWaWV3IjoxfV0sImJ1ZmZlc"
    "lZpZXdzIjpbeyJidWZmZXIiOjAsImJ5dGVPZmZzZXQiOjAsImJ5dGVMZW5ndGgiOjk2LCJ0YXJnZXQiOjQ"
    "0OTZ9LHsiYnVmZmVyIjoyLCJieXRlT2Zmc2V0Ijo5NiwiYnl0ZUxlbmd0aCI6NzIsInRhcmdldCI6MzQ5N"
    "jh9XSwiYnVmZmVycyI6W3siYnl0ZUxlbmd0aCI6MTY4fV0sIm1hdGVyaWFscyI6W3sicGJyTWV0YWxsaWN"
    "oUm91Z2huZXNzIjp7ImJhc2VDb2xvckZhY3RvciI6WzEsMCwwLDFdLCJtZXRhbGxpY0ZhY3RvciI6M319X"
    "X0AIEJJTklfAQAAAAAAAACgAQAAAgAAAAQAAADwX2I-AAAAAAAAALBfYj4AAAAAAAAAsF9iPgAAAAAAA"
    "ACwX2I-AAAAAAAAAPDfYj4AAAAAAAAA8N9iPgAAAAAAAACw32I-AAAAAAAAALBfYD8AAAAA8N9iPgAAA"
    "ADwX2A_AAAAAPDfXj8AAAAA8F9gPwAAAADw314_fX0AAAEAAwACAAMAAQAEAAUABgAFAAcABgAIAAkACgA"
    "JAAAACwAKAAwADQAOAA0AAAAPAA4AEAARABIARQAAABMAEgAUABUAFgAVAAcAFgAXAAAACAAFAAMACA="
)

model_dir = "models"
if not os.path.exists(model_dir):
    os.makedirs(model_dir)

output_path = os.path.join(model_dir, "heart.glb")

try:
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(glb_base64))
    print(f"Successfully created local 3D model at: {output_path}")
except Exception as e:
    print(f"Error creating local model: {e}")
