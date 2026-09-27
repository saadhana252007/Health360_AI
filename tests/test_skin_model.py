import torch

from ai.vision.skin.model import SkinModel


print("=" * 60)
print("        HEALTH360 SKIN MODEL TEST")
print("=" * 60)

print("\n1. CREATING MODEL")
print("-" * 60)

model = SkinModel(
    num_classes=11,
    pretrained=False
)

model.eval()

print("Model created successfully")
print("Architecture: EfficientNetV2-S")
print("Number of classes:", model.num_classes)


print("\n2. CREATING TEST INPUT")
print("-" * 60)

# Simulated preprocessed image
x = torch.randn(1, 3, 224, 224)

print("Input shape:", x.shape)
print("Input dtype:", x.dtype)


print("\n3. FORWARD PASS")
print("-" * 60)

with torch.no_grad():
    output = model(x)

print("Output shape:", output.shape)
print("Output dtype:", output.dtype)


print("\n4. EXTRACTING EMBEDDING")
print("-" * 60)

with torch.no_grad():
    embedding = model.get_embedding(x)

print("Embedding shape:", embedding.shape)
print("Embedding dtype:", embedding.dtype)


print("\n5. BASIC ASSERTIONS")
print("-" * 60)

assert output.shape == (1, 11)
assert output.dtype == torch.float32

assert embedding.shape[0] == 1
assert embedding.ndim == 2

print("Output shape check: PASSED")
print("Output dtype check: PASSED")
print("Embedding check: PASSED")


print("\n" + "=" * 60)
print("        SKIN MODEL READY")
print("=" * 60)