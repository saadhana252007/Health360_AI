import numpy as np


SYMPTOM_FEATURES = [
    "severity",
    "duration_days",
    "frequency",
    "progression",
    "site",
    "character",
    "trigger",
    "associated_symptoms",
    "pre_symptoms",
    "post_symptoms",
]


def encode_symptom(data):
    features = []

    for name in SYMPTOM_FEATURES:
        value = data.get(name, 0)

        if isinstance(value, list):
            value = len(value)

        try:
            value = float(value)
        except (TypeError, ValueError):
            value = 0.0

        features.append(value)

    return np.array(features, dtype=np.float32)