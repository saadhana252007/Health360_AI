import numpy as np


class UncertaintyEstimator:

    def __init__(self):
        pass

    def entropy(self, probabilities):
        probabilities = np.asarray(probabilities, dtype=np.float32)
        probabilities = np.clip(probabilities, 1e-8, 1.0)
        probabilities = probabilities / probabilities.sum()
        return float(-np.sum(probabilities * np.log(probabilities)))

    def normalized_entropy(self, probabilities):
        probabilities = np.asarray(probabilities, dtype=np.float32)

        n = len(probabilities)

        if n <= 1:
            return 0.0

        return self.entropy(probabilities) / np.log(n)

    def prediction_confidence(self, probabilities):
        probabilities = np.asarray(probabilities, dtype=np.float32)
        return float(np.max(probabilities))

    def estimate(
        self,
        probabilities,
        modality_completeness,
        image_quality=None
    ):
        confidence = self.prediction_confidence(probabilities)

        uncertainty = self.normalized_entropy(probabilities)

        completeness = float(
            np.clip(modality_completeness, 0.0, 1.0)
        )

        if image_quality is None:
            quality = 1.0
        else:
            quality = float(
                np.clip(image_quality, 0.0, 1.0)
            )

        adjusted_confidence = (
            confidence
            * completeness
            * quality
        )

        return {
            "confidence": adjusted_confidence,
            "uncertainty": uncertainty,
            "completeness": completeness,
            "image_quality": quality
        }