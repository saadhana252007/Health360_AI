import torch

from ai.vision.wound.model import WoundModel


print("=" * 60)
print("        HEALTH360 WOUND MODEL TEST")
print("=" * 60)

print("\n1. CREATING MODEL")
print("-" * 60)

model = WoundModel(
    num_classes=8,
    pretrained=False
)

model.eval()

print("Model created successfully")
print("Architecture: U-Net + EfficientNet-B3")
print("Number of wound classes:", model.num_classes)


print("\n2. CREATING TEST INPUT")
print("-" * 60)

x = torch.randn(1, 3, 224, 224)

print("Input shape:", x.shape)
print("Input dtype:", x.dtype)


print("\n3. FORWARD PASS")
print("-" * 60)

with torch.no_grad():
    result = model(x)

segmentation = result["segmentation"]
classification = result["classification"]

print("Segmentation output shape:", segmentation.shape)
print("Classification output shape:", classification.shape)


print("\n4. EXTRACTING EMBEDDING")
print("-" * 60)

with torch.no_grad():
    embedding = model.get_embedding(x)

print("Embedding shape:", embedding.shape)
print("Embedding dtype:", embedding.dtype)


print("\n5. BASIC ASSERTIONS")
print("-" * 60)

assert segmentation.shape == (1, 1, 224, 224)
assert classification.shape == (1, 8)

assert segmentation.dtype == torch.float32
assert classification.dtype == torch.float32

assert embedding.shape[0] == 1
assert embedding.ndim == 2
assert embedding.dtype == torch.float32

print("Segmentation shape check: PASSED")
print("Classification shape check: PASSED")
print("Output dtype checks: PASSED")
print("Embedding check: PASSED")


print("\n" + "=" * 60)
print("        WOUND MODEL READY")
print("=" * 60)