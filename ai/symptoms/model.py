import numpy as np
import xgboost as xgb


class SymptomModel:

    def __init__(self, num_features=10):
        self.num_features = num_features
        self.model = xgb.XGBRegressor(
            n_estimators=50,
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

        prediction = self.model.predict(X)

        return prediction

    def transform_result(self, prediction):
        score = float(np.clip(prediction[0], 0.0, 1.0))

        return {
            "model": "symptom_v1",
            "version": "1.0",
            "symptom_score": score,
            "confidence": 0.0,
            "uncertainty": 0.0
        }