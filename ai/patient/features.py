from datetime import date, datetime
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


def calculate_age(date_of_birth):
    if not date_of_birth:
        return 0.0

    try:
        birth_date = datetime.strptime(
            str(date_of_birth),
            "%Y-%m-%d"
        ).date()

        today = date.today()

        age = today.year - birth_date.year

        if (today.month, today.day) < (
            birth_date.month,
            birth_date.day
        ):
            age -= 1

        return float(age)

    except (TypeError, ValueError):
        return 0.0


def calculate_bmi(height_cm, weight_kg):
    try:
        height = float(height_cm)
        weight = float(weight_kg)

        if height <= 0 or weight <= 0:
            return 0.0

        height_m = height / 100.0

        return float(weight / (height_m ** 2))

    except (TypeError, ValueError):
        return 0.0


def encode_patient(data):

    data = dict(data)

    if "age" not in data:
        data["age"] = calculate_age(
            data.get("date_of_birth")
        )

    if "bmi" not in data:
        data["bmi"] = calculate_bmi(
            data.get("height_cm"),
            data.get("weight_kg")
        )

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

    return np.array(
        features,
        dtype=np.float32
    )