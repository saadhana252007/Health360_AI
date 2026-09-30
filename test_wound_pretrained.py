import sys
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

image_path = sys.argv[1]

model_name = "Hemgg/wound-image-classification"

processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)
model.eval()

image = Image.open(image_path).convert("RGB")

inputs = processor(
    images=image,
    return_tensors="pt"
)

with torch.no_grad():
    outputs = model(**inputs)

probabilities = torch.softmax(outputs.logits, dim=1)[0]
index = int(torch.argmax(probabilities))

print("\nWOUND MODEL RESULT")
print("------------------")
print("Finding:", model.config.id2label[index])
print("Confidence:", round(float(probabilities[index]) * 100, 2), "%")
print("\nProbabilities:")

for i, probability in enumerate(probabilities):
    print(
        model.config.id2label[i],
        ":",
        round(float(probability) * 100, 2),
        "%"
    )