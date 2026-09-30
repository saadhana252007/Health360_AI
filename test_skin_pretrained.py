import sys
import torch
from PIL import Image
from torchvision import transforms
from ai.vision.skin.model import SkinModel

image_path = sys.argv[1]

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

image = Image.open(image_path).convert("RGB")
tensor = transform(image).unsqueeze(0)

model = SkinModel()
model.eval()

result = model.predict(tensor)

print("\nSKIN MODEL RESULT")
print("-----------------")
print("Finding:", result["class_name"])
print("Confidence:", round(result["confidence"] * 100, 2), "%")
print("\nProbabilities:")

for name, probability in result["probabilities"].items():
    print(name, ":", round(probability * 100, 2), "%")