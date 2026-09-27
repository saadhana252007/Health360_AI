import numpy as np

from ai.symptoms.features import encode_symptom
from ai.symptoms.model import SymptomModel


print("=" * 60)
print("        HEALTH360 SYMPTOM MODEL TEST")
print("=" * 60)

print("\n1. ENCODING SYMPTOM")
print("-" * 60)

symptom = {
    "severity": 7,
    "duration_days": 5,
    "frequency": 3,
    "progression": 1,
    "site": 2,
    "character": 4,
    "trigger": 1,
    "associated_symptoms": ["nausea", "light_sensitivity"],
    "pre_symptoms": [],
    "post_symptoms": ["fatigue"]
}

features = encode_symptom(symptom)

print("Feature vector:", features)
print("Feature shape:", features.shape)


print("\n2. CREATING MODEL")
print("-" * 60)

model = SymptomModel(num_features=10)

print("Model created successfully")
print("Model: XGBoost")
print("Number of features:", model.num_features)


print("\n3. CREATING TEST DATA")
print("-" * 60)

X = np.random.rand(20, 10).astype(np.float32)
y = np.random.rand(20).astype(np.float32)

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

assert features.shape == (10,)
assert prediction.shape == (1,)
assert 0.0 <= result["symptom_score"] <= 1.0

print("Feature encoding: PASSED")
print("Prediction shape: PASSED")
print("Result validation: PASSED")


print("\n" + "=" * 60)
print("        SYMPTOM MODEL READY")
print("=" * 60)