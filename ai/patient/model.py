import numpy as np
import pandas as pd
import joblib
from huggingface_hub import hf_hub_download


class PatientRiskModel:
    def __init__(self):
        model_path = hf_hub_download(
            repo_id="kiselyovd/cardio-risk-rf",
            filename="cardio_risk_rf.joblib"
        )

        loaded = joblib.load(model_path)
        self.model = loaded["model"]

    def predict(self, data):
        age = float(data[0, 0])
        sex = float(data[0, 1])
        bmi = float(data[0, 2])
        systolic_bp = float(data[0, 4])
        diastolic_bp = float(data[0, 5])
        activity = float(data[0, 21])
        tobacco = float(data[0, 22])
        alcohol = float(data[0, 23])

        height = 170.0
        weight = bmi * (height / 100.0) ** 2

        features = pd.DataFrame([{
            "age": age,
            "gender": sex,
            "height": height,
            "weight": weight,
            "ap_hi": systolic_bp,
            "ap_lo": diastolic_bp,
            "cholesterol": 1.0,
            "gluc": 1.0,
            "smoke": tobacco,
            "alco": alcohol,
            "active": activity
        }])

        probabilities = self.model.predict_proba(features)[0]

        index = int(np.argmax(probabilities))

        class_names = {
            0: "No cardiovascular disease",
            1: "Cardiovascular disease"
        }

        return {
            "class_index": index,
            "class_name": class_names[index],
            "confidence": float(probabilities[index]),
            "probabilities": {
                class_names[int(self.model.classes_[i])]: float(
                    probabilities[i]
                )
                for i in range(len(probabilities))
            }
        }