import numpy as np


PATIENT_FEATURES = [
    "age",
    "sex",
    "bmi",
    "heart_rate",
    "systolic_bp",
    "diastolic_bp",
    "spo2",
    "temperature",
    "diabetes",
    "hypertension",
    "asthma",
    "heart_disease",
    "kidney_disease",
    "liver_disease",
    "thyroid",
    "previous_cancer",
    "family_diabetes",
    "family_heart_disease",
    "family_hypertension",
    "family_cancer",
    "sleep_hours",
    "activity_level",
    "tobacco",
    "alcohol",
    "stress_level",
]


def encode_patient(data):
    features = []

    for name in PATIENT_FEATURES:
        value = data.get(name, None)

        if value is None:
            features.append(0.0)
            continue

        if isinstance(value, bool):
            value = float(value)

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        features.append(value)

    return np.array(features, dtype=np.float32)