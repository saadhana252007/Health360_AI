import torch
import numpy as np
import cv2

from ai.common.preprocessing import preprocess_image, get_inference_transform
from ai.vision.skin.model import SkinModel
from ai.vision.oral.model import OralModel
from ai.vision.wound.model import WoundModel
from ai.symptoms.features import encode_symptom
from ai.symptoms.model import SymptomModel
from ai.patient.features import encode_patient
from ai.patient.model import PatientRiskModel
from ai.fusion.model import MultimodalFusion
from ai.uncertainty.model import UncertaintyEstimator


class AIService:
    def __init__(self):
        self.device = torch.device("cpu")

        self.skin_model = SkinModel(num_classes=11, pretrained=False).to(self.device)
        self.oral_model = OralModel(num_classes=4, pretrained=False).to(self.device)
        self.wound_model = WoundModel(num_classes=8, pretrained=False).to(self.device)

        self.symptom_model = SymptomModel()
        self.patient_model = PatientRiskModel()

        self.fusion_model = MultimodalFusion().to(self.device)
        self.uncertainty_estimator = UncertaintyEstimator()

        self.skin_model.eval()
        self.oral_model.eval()
        self.wound_model.eval()
        self.fusion_model.eval()

        self._fit_test_models()

    def _fit_test_models(self):
        rng = np.random.default_rng(42)

        symptom_x = rng.random((100, 10), dtype=np.float32)
        symptom_y = rng.random(100, dtype=np.float32)
        self.symptom_model.fit(symptom_x, symptom_y)

        patient_x = rng.random((100, 25), dtype=np.float32)
        patient_y = rng.random(100, dtype=np.float32)
        self.patient_model.fit(patient_x, patient_y)

    def _analyze_image(self, image, image_type):
        tensor = preprocess_image(image, get_inference_transform()).to(self.device)

        with torch.no_grad():
            if image_type == "skin":
                output = self.skin_model(tensor)
                embedding = self.skin_model.get_embedding(tensor)
                return {
                    "type": "skin",
                    "prediction": output.cpu().numpy().tolist(),
                    "embedding": embedding.cpu().numpy().tolist()
                }

            if image_type == "oral":
                output = self.oral_model(tensor)
                embedding = self.oral_model.get_embedding(tensor)
                return {
                    "type": "oral",
                    "prediction": output.cpu().numpy().tolist(),
                    "embedding": embedding.cpu().numpy().tolist()
                }

            if image_type == "wound":
                output = self.wound_model(tensor)
                embedding = self.wound_model.get_embedding(tensor)
                return {
                    "type": "wound",
                    "segmentation": output["segmentation"].cpu().numpy().tolist(),
                    "classification": output["classification"].cpu().numpy().tolist(),
                    "embedding": embedding.cpu().numpy().tolist()
                }

        raise ValueError(f"Unsupported image type: {image_type}")

    def analyze(self, image=None, image_type=None, symptoms=None, patient=None):
        symptom_features = encode_symptom(symptoms or {})
        patient_features = encode_patient(patient or {})

        symptom_result = self.symptom_model.transform_result(
            self.symptom_model.predict(symptom_features.reshape(1, -1))
        )

        patient_result = self.patient_model.transform_result(
            self.patient_model.predict(patient_features.reshape(1, -1))
        )

        image_result = None
        image_embedding = None
        image_key = None

        if image is not None and image_type is not None:
            image_result = self._analyze_image(image, image_type)
            image_embedding = torch.tensor(
                image_result["embedding"],
                dtype=torch.float32,
                device=self.device
            )

            image_key = image_type

        modality_inputs = {
            "skin": torch.zeros((1, 1280), device=self.device),
            "oral": torch.zeros((1, 512), device=self.device),
            "wound": torch.zeros((1, 384), device=self.device),
            "symptom": torch.tensor(
                symptom_features.reshape(1, -1),
                dtype=torch.float32,
                device=self.device
            ),
            "patient": torch.tensor(
                patient_features.reshape(1, -1),
                dtype=torch.float32,
                device=self.device
            )
        }

        modality_mask = torch.tensor(
            [[0.0, 0.0, 0.0, 1.0, 1.0]],
            dtype=torch.float32,
            device=self.device
        )

        if image_key == "skin":
            modality_inputs["skin"] = image_embedding
            modality_mask[0, 0] = 1.0

        elif image_key == "oral":
            modality_inputs["oral"] = image_embedding
            modality_mask[0, 1] = 1.0

        elif image_key == "wound":
            modality_inputs["wound"] = image_embedding
            modality_mask[0, 2] = 1.0

        with torch.no_grad():
            fusion_result = self.fusion_model(
                skin=modality_inputs["skin"],
                oral=modality_inputs["oral"],
                wound=modality_inputs["wound"],
                symptoms=modality_inputs["symptom"],
                patient=modality_inputs["patient"],
                modality_mask=modality_mask
            )

        health_vector = fusion_result["health_vector"].cpu().numpy()

        uncertainty_result = self.uncertainty_estimator.estimate(
            health_vector[0],
            modality_completeness=float(
                fusion_result["completeness"].item()
            ),
            image_quality=1.0
        )
        

        return {
            "image_result": image_result,
            "symptom_result": symptom_result,
            "patient_result": patient_result,
            "fusion_result": {
                "health_vector": health_vector.tolist(),
                "confidence": float(fusion_result["confidence"].item()),
                "completeness": float(fusion_result["completeness"].item()),
                "gates": fusion_result["gates"].cpu().numpy().tolist()
            },
            "uncertainty": uncertainty_result
        }
    