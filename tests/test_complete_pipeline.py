import numpy as np
import torch

from ai.common.preprocessing import get_inference_transform, preprocess_image
from ai.vision.skin.model import SkinModel
from ai.vision.oral.model import OralModel
from ai.vision.wound.model import WoundModel
from ai.symptoms.features import encode_symptom
from ai.symptoms.model import SymptomModel
from ai.patient.features import encode_patient
from ai.patient.model import PatientRiskModel
from ai.fusion.model import MultimodalFusion
from ai.uncertainty.model import UncertaintyEstimator


print("=" * 70)
print("        HEALTH360 COMPLETE AI PIPELINE TEST")
print("=" * 70)


print("\n1. IMAGE PREPROCESSING")
print("-" * 70)

image = np.random.randint(
    0,
    256,
    (512, 512, 3),
    dtype=np.uint8
)

transform = get_inference_transform()

image_tensor = preprocess_image(
    image,
    transform
)

print("Input image:", image.shape)
print("Preprocessed image:", image_tensor.shape)


print("\n2. VISION MODELS")
print("-" * 70)

skin_model = SkinModel(
    num_classes=11,
    pretrained=False
)

oral_model = OralModel(
    num_classes=4,
    pretrained=False
)

wound_model = WoundModel(
    num_classes=8,
    pretrained=False
)

skin_model.eval()
oral_model.eval()
wound_model.eval()

with torch.no_grad():
    skin_output = skin_model(image_tensor)
    skin_embedding = skin_model.get_embedding(image_tensor)

    oral_output = oral_model(image_tensor)
    oral_embedding = oral_model.get_embedding(image_tensor)

    wound_result = wound_model(image_tensor)
    wound_embedding = wound_model.get_embedding(image_tensor)

print("Skin output:", skin_output.shape)
print("Skin embedding:", skin_embedding.shape)

print("Oral output:", oral_output.shape)
print("Oral embedding:", oral_embedding.shape)

print("Wound segmentation:", wound_result["segmentation"].shape)
print("Wound classification:", wound_result["classification"].shape)
print("Wound embedding:", wound_embedding.shape)


print("\n3. SYMPTOM MODEL")
print("-" * 70)

symptom_data = {
    "severity": 6,
    "duration_days": 4,
    "frequency": 3,
    "progression": 1,
    "site": 2,
    "character": 3,
    "trigger": 1,
    "associated_symptoms": ["fatigue"],
    "pre_symptoms": [],
    "post_symptoms": ["weakness"]
}

symptom_features = encode_symptom(symptom_data)

symptom_model = SymptomModel(
    num_features=10
)

X_symptom = np.random.rand(
    20,
    10
).astype(np.float32)

y_symptom = np.random.rand(
    20
).astype(np.float32
)

symptom_model.fit(
    X_symptom,
    y_symptom
)

symptom_prediction = symptom_model.predict(
    symptom_features.reshape(1, -1)
)

symptom_result = symptom_model.transform_result(
    symptom_prediction
)

print("Symptom features:", symptom_features.shape)
print("Symptom result:", symptom_result)


print("\n4. PATIENT RISK MODEL")
print("-" * 70)

patient_data = {
    "age": 30,
    "sex": 1,
    "bmi": 23.5,
    "heart_rate": 78,
    "systolic_bp": 120,
    "diastolic_bp": 80,
    "spo2": 98,
    "temperature": 36.7,
    "diabetes": 0,
    "hypertension": 0,
    "asthma": 0,
    "heart_disease": 0,
    "kidney_disease": 0,
    "liver_disease": 0,
    "thyroid": 0,
    "previous_cancer": 0,
    "family_diabetes": 0,
    "family_heart_disease": 0,
    "family_hypertension": 0,
    "family_cancer": 0,
    "sleep_hours": 7,
    "activity_level": 3,
    "tobacco": 0,
    "alcohol": 0,
    "stress_level": 2
}

patient_features = encode_patient(
    patient_data
)

patient_model = PatientRiskModel(
    num_features=25
)

X_patient = np.random.rand(
    30,
    25
).astype(np.float32)

y_patient = np.random.rand(
    30
).astype(np.float32)

patient_model.fit(
    X_patient,
    y_patient
)

patient_prediction = patient_model.predict(
    patient_features.reshape(1, -1)
)

patient_result = patient_model.transform_result(
    patient_prediction
)

print("Patient features:", patient_features.shape)
print("Patient result:", patient_result)


print("\n5. MULTIMODAL FUSION")
print("-" * 70)

fusion_model = MultimodalFusion()

fusion_model.eval()

modality_mask = torch.tensor(
    [[1.0, 1.0, 1.0, 1.0, 1.0]]
)

with torch.no_grad():
    fusion_result = fusion_model(
        skin=skin_embedding,
        oral=oral_embedding,
        wound=wound_embedding,
        symptoms=torch.from_numpy(
            symptom_features
        ).reshape(1, -1),
        patient=torch.from_numpy(
            patient_features
        ).reshape(1, -1),
        modality_mask=modality_mask
    )

print(
    "Health vector:",
    fusion_result["health_vector"]
)

print(
    "Fusion confidence:",
    fusion_result["confidence"]
)

print(
    "Completeness:",
    fusion_result["completeness"]
)

print(
    "Modality gates:",
    fusion_result["gates"]
)


print("\n6. UNCERTAINTY")
print("-" * 70)

uncertainty_estimator = UncertaintyEstimator()

health_probabilities = (
    fusion_result["health_vector"]
    .squeeze(0)
    .detach()
    .numpy()
)

health_probabilities = (
    health_probabilities
    / health_probabilities.sum()
)

uncertainty_result = uncertainty_estimator.estimate(
    probabilities=health_probabilities,
    modality_completeness=float(
        fusion_result["completeness"][0, 0]
    ),
    image_quality=1.0
)

print("Uncertainty result:", uncertainty_result)


print("\n7. FINAL ASSERTIONS")
print("-" * 70)

assert image_tensor.shape == (1, 3, 224, 224)

assert skin_output.shape == (1, 11)
assert skin_embedding.shape == (1, 1280)

assert oral_output.shape == (1, 4)
assert oral_embedding.shape == (1, 512)

assert wound_result["segmentation"].shape == (
    1,
    1,
    224,
    224
)

assert wound_result["classification"].shape == (
    1,
    8
)

assert wound_embedding.shape == (1, 384)

assert symptom_features.shape == (10,)
assert patient_features.shape == (25,)

assert fusion_result["health_vector"].shape == (1, 7)

assert (
    0.0
    <= uncertainty_result["confidence"]
    <= 1.0
)

assert (
    0.0
    <= uncertainty_result["uncertainty"]
    <= 1.0
)

print("Image preprocessing: PASSED")
print("Skin model: PASSED")
print("Oral model: PASSED")
print("Wound model: PASSED")
print("Symptom model: PASSED")
print("Patient risk model: PASSED")
print("Fusion model: PASSED")
print("Uncertainty model: PASSED")


print("\n" + "=" * 70)
print("        HEALTH360 COMPLETE AI PIPELINE READY")
print("=" * 70)