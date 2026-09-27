import torch

from ai.fusion.model import MultimodalFusion


print("=" * 60)
print("        HEALTH360 MULTIMODAL FUSION TEST")
print("=" * 60)

print("\n1. CREATING MODEL")
print("-" * 60)

model = MultimodalFusion()

model.eval()

print("Fusion model created successfully")
print("Architecture: Gated MLP")


print("\n2. CREATING TEST FEATURES")
print("-" * 60)

skin = torch.randn(1, 1280)
oral = torch.randn(1, 512)
wound = torch.randn(1, 384)
symptoms = torch.randn(1, 10)
patient = torch.randn(1, 25)

modality_mask = torch.tensor(
    [[1.0, 0.0, 0.0, 1.0, 1.0]]
)

print("Skin:", skin.shape)
print("Oral:", oral.shape)
print("Wound:", wound.shape)
print("Symptoms:", symptoms.shape)
print("Patient:", patient.shape)
print("Modality mask:", modality_mask.shape)


print("\n3. FORWARD PASS")
print("-" * 60)

with torch.no_grad():
    result = model(
        skin=skin,
        oral=oral,
        wound=wound,
        symptoms=symptoms,
        patient=patient,
        modality_mask=modality_mask
    )

print("Health vector:", result["health_vector"].shape)
print("Confidence:", result["confidence"].shape)
print("Completeness:", result["completeness"].shape)
print("Gates:", result["gates"].shape)


print("\n4. OUTPUT VALUES")
print("-" * 60)

print("Health vector:", result["health_vector"])
print("Confidence:", result["confidence"])
print("Completeness:", result["completeness"])
print("Gates:", result["gates"])


print("\n5. BASIC ASSERTIONS")
print("-" * 60)

assert result["health_vector"].shape == (1, 7)
assert result["confidence"].shape == (1, 1)
assert result["completeness"].shape == (1, 1)
assert result["gates"].shape == (1, 5)

assert torch.all(
    result["health_vector"] >= 0
)

assert torch.all(
    result["health_vector"] <= 1
)

assert torch.all(
    result["gates"][:, 1] == 0
)

assert torch.all(
    result["gates"][:, 2] == 0
)

print("Health vector check: PASSED")
print("Confidence check: PASSED")
print("Completeness check: PASSED")
print("Missing modality handling: PASSED")


print("\n" + "=" * 60)
print("        MULTIMODAL FUSION READY")
print("=" * 60)