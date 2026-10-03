
import torch

from transformers import AutoImageProcessor, AutoModelForImageClassification

from ai.common.preprocessing import preprocess_image, get_inference_transform
from ai.vision.skin.model import SkinModel
from ai.vision.oral.model import OralModel
from ai.symptoms.model import SymptomModel
from ai.patient.features import encode_patient
from ai.patient.model import PatientRiskModel
from ai.fusion.model import MultimodalFusion
from backend.services.interpretation_service import InterpretationService


class AIService:

    def __init__(self):
        self.device = torch.device("cpu")
        self._skin_model = None
        self._oral_model = None
        self._wound_processor = None
        self._wound_model = None
        self._symptom_model = None
        self._patient_model = None
        self._fusion_model = None
        self.interpretation_service = InterpretationService()

    def _get_skin_model(self):
        if self._skin_model is None:
            self._skin_model = SkinModel(
                num_classes=5,
                pretrained=False
            ).to(self.device)
            self._skin_model.eval()

        return self._skin_model

    def _get_oral_model(self):
        if self._oral_model is None:
            self._oral_model = OralModel(
                num_classes=6,
                pretrained=False
            ).to(self.device)
            self._oral_model.eval()

        return self._oral_model

    def _get_wound_model(self):
        if self._wound_model is None:
            self._wound_processor = AutoImageProcessor.from_pretrained(
                "Hemgg/wound-image-classification"
            )

            self._wound_model = AutoModelForImageClassification.from_pretrained(
                "Hemgg/wound-image-classification"
            ).to(self.device)

            self._wound_model.eval()

        return self._wound_model

    def _get_symptom_model(self):
        if self._symptom_model is None:
            self._symptom_model = SymptomModel()

        return self._symptom_model

    def _get_patient_model(self):
        if self._patient_model is None:
            self._patient_model = PatientRiskModel()

        return self._patient_model

    def _get_fusion_model(self):
        if self._fusion_model is None:
            self._fusion_model = MultimodalFusion()

        return self._fusion_model

    def _analyze_image(self, image, image_type):
        tensor = preprocess_image(
            image,
            get_inference_transform()
        ).to(self.device)

        with torch.no_grad():

            if image_type == "skin":
                prediction = self._get_skin_model().predict(tensor)

                return {
                    "type": "skin",
                    "prediction": prediction
                }

            if image_type == "oral":
                prediction = self._get_oral_model().predict(tensor)

                return {
                    "type": "oral",
                    "prediction": prediction
                }

            if image_type == "wound":
                model = self._get_wound_model()

                inputs = self._wound_processor(
                    images=image,
                    return_tensors="pt"
                )

                inputs = {
                    key: value.to(self.device)
                    for key, value in inputs.items()
                }

                outputs = model(**inputs)

                probabilities = torch.softmax(
                    outputs.logits,
                    dim=1
                )[0]

                index = int(
                    torch.argmax(probabilities).item()
                )

                probabilities_dict = {
                    model.config.id2label[i]: float(
                        probabilities[i].item()
                    )
                    for i in range(len(probabilities))
                }

                return {
                    "type": "wound",
                    "prediction": {
                        "class_index": index,
                        "class_name": model.config.id2label[index],
                        "confidence": float(
                            probabilities[index].item()
                        ),
                        "probabilities": probabilities_dict
                    }
                }

        raise ValueError(
            f"Unsupported image type: {image_type}"
        )

    def analyze(
        self,
        image=None,
        image_type=None,
        symptoms=None,
        patient=None
    ):
        symptoms = symptoms or {}
        patient = patient or {}

        symptom_text = self._build_symptom_text(symptoms)

        symptom_result = self._get_symptom_model().predict_text(
            symptom_text
        )

        patient_features = encode_patient(patient)

        patient_result = self._get_patient_model().predict(
            patient_features.reshape(1, -1)
        )

        image_result = None

        if image is not None and image_type is not None:
            image_result = self._analyze_image(
                image,
                image_type
            )

        fusion_result = self._get_fusion_model().fuse(
            image_result=image_result,
            symptom_result=symptom_result,
            patient_result=patient_result,
            patient=patient
        )

        confidences = []

        if image_result:
            confidences.append(
                float(
                    image_result["prediction"].get(
                        "confidence",
                        0.0
                    )
                )
            )

        confidences.append(
            float(symptom_result.get("confidence", 0.0))
        )

        confidences.append(
            float(patient_result.get("confidence", 0.0))
        )

        overall_confidence = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        uncertainty = {
            "confidence": overall_confidence,
            "uncertainty": 1.0 - overall_confidence,
            "completeness": self._calculate_completeness(
                symptoms,
                patient
            ),
            "image_quality": 1.0 if image is not None else None
        }

        screening = self.interpretation_service.interpret(
            symptoms=symptoms,
            patient=patient,
            symptom_result=symptom_result,
            patient_result=patient_result,
            image_result=image_result,
            fusion_result=fusion_result,
            uncertainty=uncertainty
        )

        return {
            "image_result": image_result,
            "symptom_result": symptom_result,
            "patient_result": patient_result,
            "fusion_result": fusion_result,
            "uncertainty": uncertainty,
            "screening": screening
        }

    def _calculate_completeness(self, symptoms, patient):
        required_sections = 3
        completed_sections = 0

        profile_fields = [
            "full_name",
            "date_of_birth",
            "sex",
            "height_cm",
            "weight_kg"
        ]

        vital_fields = [
            "heart_rate",
            "systolic_bp",
            "diastolic_bp",
            "spo2",
            "temperature"
        ]

        has_profile = any(
            patient.get(field) not in [None, ""]
            for field in profile_fields
        )

        has_vitals = any(
            patient.get(field) not in [None, ""]
            for field in vital_fields
        )

        if has_profile:
            completed_sections += 1

        if has_vitals:
            completed_sections += 1

        if symptoms:
            completed_sections += 1

        return completed_sections / required_sections

    def _build_symptom_text(self, symptoms):
        if not symptoms:
            return "No symptoms reported."

        parts = []

        for key, value in symptoms.items():
            if value is not None and str(value).strip():
                parts.append(f"{key}: {value}")

        if not parts:
            return "No symptoms reported."

        return ". ".join(parts)
