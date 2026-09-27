import numpy as np
import xgboost as xgb


class PatientRiskModel:

    def __init__(self, num_features=25):
        self.num_features = num_features

        self.model = xgb.XGBRegressor(
            n_estimators=100,
            max_depth=3,
            learning_rate=0.05,
            objective="reg:squarederror",
            random_state=42
        )

    def fit(self, X, y):
        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32)

        self.model.fit(X, y)

    def predict(self, X):
        X = np.asarray(X, dtype=np.float32)

        return self.model.predict(X)

    def transform_result(self, prediction):
        score = float(np.clip(prediction[0], 0.0, 1.0))

        return {
            "model": "patient_risk_v1",
            "version": "1.0",
            "risk_score": score,
            "confidence": 0.0,
            "uncertainty": 0.0
        }