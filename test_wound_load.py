from transformers import AutoImageProcessor, AutoModelForImageClassification

model_name = "Hemgg/wound-image-classification"

processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

print("WOUND MODEL LOADED")
print(model.config.id2label)