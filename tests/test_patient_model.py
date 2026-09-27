import numpy as np

from ai.patient.features import encode_patient
from ai.patient.model import PatientRiskModel


print("=" * 60)
print("        HEALTH360 PATIENT RISK MODEL TEST")
print("=" * 60)

print("\n1. ENCODING PATIENT DATA")
print("-" * 60)

patient = {
    "age": 45,
    "sex": 1,
    "bmi": 27.5,
    "heart_rate": 82,
    "systolic_bp": 135,
    "diastolic_bp": 88,
    "spo2": 98,
    "temperature": 36.8,
    "diabetes": 0,
    "hypertension": 1,
    "asthma": 0,
    "heart_disease": 0,
    "kidney_disease": 0,
    "liver_disease": 0,
    "thyroid": 0,
    "previous_cancer": 0,
    "family_diabetes": 1,
    "family_heart_disease": 0,
    "family_hypertension": 1,
    "family_cancer": 0,
    "sleep_hours": 6,
    "activity_level": 2,
    "tobacco": 0,
    "alcohol": 1,
    "stress_level": 3
}

features = encode_patient(patient)

print("Feature vector:", features)
print("Feature shape:", features.shape)


print("\n2. CREATING MODEL")
print("-" * 60)

model = PatientRiskModel(num_features=25)

print("Model created successfully")
print("Model: XGBoost")
print("Number of features:", model.num_features)


print("\n3. CREATING TEST DATA")
print("-" * 60)

X = np.random.rand(30, 25).astype(np.float32)
y = np.random.rand(30).astype(np.float32)

print("Training data shape:", X.shape)
print("Target shape:", y.shape)


print("\n4. TRAINING")
print("-" * 60)

model.fit(X, y)

print("Training completed")


print("\n5. PREDICTION")
print("-" * 60)

prediction = model.predict(
    features.reshape(1, -1)
)

print("Prediction:", prediction)


print("\n6. RESULT TRANSFORMATION")
print("-" * 60)

result = model.transform_result(prediction)

print("Result:", result)


print("\n7. BASIC ASSERTIONS")
print("-" * 60)

assert features.shape == (25,)
assert prediction.shape == (1,)
assert 0.0 <= result["risk_score"] <= 1.0

print("Feature encoding: PASSED")
print("Prediction shape: PASSED")
print("Result validation: PASSED")


print("\n" + "=" * 60)
print("        PATIENT RISK MODEL READY")
print("=" * 60)