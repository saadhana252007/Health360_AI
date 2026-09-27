import torch

from ai.vision.oral.model import OralModel


print("=" * 60)
print("        HEALTH360 ORAL MODEL TEST")
print("=" * 60)

print("\n1. CREATING MODEL")
print("-" * 60)

model = OralModel(
    num_classes=4,
    pretrained=False
)

model.eval()

print("Model created successfully")
print("Architecture: ResNet18")
print("Number of classes:", model.num_classes)


print("\n2. CREATING TEST INPUT")
print("-" * 60)

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

assert output.shape == (1, 4)
assert output.dtype == torch.float32

assert embedding.shape == (1, 512)
assert embedding.dtype == torch.float32

print("Output shape check: PASSED")
print("Output dtype check: PASSED")
print("Embedding shape check: PASSED")
print("Embedding dtype check: PASSED")


print("\n" + "=" * 60)
print("        ORAL MODEL READY")
print("=" * 60)
