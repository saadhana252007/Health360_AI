
import gc
import threading

import cv2
import numpy as np

from backend.services.interpretation_service import InterpretationService


class AIService:
    def __init__(self):
        self.device = "cpu"

        self._skin_model = None
        self._oral_model = None
        self._wound_processor = None
        self._wound_model = None
        self._symptom_model = None
        self._patient_model = None
        self._fusion_model = None

        self._inference_lock = threading.Lock()

        self.interpretation_service = InterpretationService()

    def _get_skin_model(self):
        if self._skin_model is None:
            from ai.vision.skin.model import SkinModel

            self._skin_model = SkinModel(
                num_classes=5,
                pretrained=False
            )
            self._skin_model.eval()

        return self._skin_model

    def _get_oral_model(self):
        if self._oral_model is None:
            from ai.vision.oral.model import OralModel

            self._oral_model = OralModel(
                num_classes=6,
                pretrained=False
            )
            self._oral_model.eval()

        return self._oral_model

    def _get_wound_model(self):
        if self._wound_model is None:
            from transformers import (
                AutoImageProcessor,
                AutoModelForImageClassification
            )

            model_name = "Hemgg/wound-image-classification"

            self._wound_processor = (
                AutoImageProcessor.from_pretrained(model_name)
            )

            self._wound_model = (
                AutoModelForImageClassification.from_pretrained(
                    model_name
                )
            )
            self._wound_model.eval()

        return self._wound_model

    def _get_symptom_model(self):
        if self._symptom_model is None:
            from ai.symptoms.model import SymptomModel

            self._symptom_model = SymptomModel()

        return self._symptom_model

    def _get_patient_model(self):
        if self._patient_model is None:
            from ai.patient.model import PatientRiskModel

            self._patient_model = PatientRiskModel()

        return self._patient_model

    def _get_fusion_model(self):
        if self._fusion_model is None:
            from ai.fusion.model import MultimodalFusion

            self._fusion_model = MultimodalFusion()

        return self._fusion_model

    def _release_model(self, model_type):
        if model_type == "skin":
            self._skin_model = None

        elif model_type == "oral":
            self._oral_model = None

        elif model_type == "wound":
            self._wound_model = None
            self._wound_processor = None

        elif model_type == "symptom":
            self._symptom_model = None

        elif model_type == "patient":
            self._patient_model = None

        gc.collect()

    def _release_all_models(self):
        self._skin_model = None
        self._oral_model = None
        self._wound_processor = None
        self._wound_model = None
        self._symptom_model = None
        self._patient_model = None

        gc.collect()


    def _analyze_image(self, image, image_type):
        import torch
        from PIL import Image

        from ai.common.preprocessing import (
            preprocess_image,
            get_inference_transform
        )

        try:
            if image_type == "skin":
                tensor = preprocess_image(
                    image,
                    get_inference_transform()
                )

                model = self._get_skin_model()

                with torch.inference_mode():
                    prediction = model.predict(tensor)

                return {
                    "type": "skin",
                    "prediction": prediction
                }

            elif image_type == "oral":
                tensor = preprocess_image(
                    image,
                    get_inference_transform()
                )

                model = self._get_oral_model()

                with torch.inference_mode():
                    prediction = model.predict(tensor)

                return {
                    "type": "oral",
                    "prediction": prediction
                }

            elif image_type == "wound":
                model = self._get_wound_model()
                processor = self._wound_processor

                rgb_image = cv2.cvtColor(
                    image,
                    cv2.COLOR_BGR2RGB
                )
                pil_image = Image.fromarray(rgb_image)

                inputs = processor(
                    images=pil_image,
                    return_tensors="pt"
                )

                with torch.inference_mode():
                    outputs = model(**inputs)
                    probabilities = torch.softmax(
                        outputs.logits,
                        dim=1
                    )[0]

                index = int(
                    torch.argmax(probabilities).item()
                )

                labels = model.config.id2label

                result = {
                    "type": "wound",
                    "prediction": {
                        "class_index": index,
                        "class_name": labels[index],
                        "confidence": float(
                            probabilities[index].item()
                        ),
                        "probabilities": {
                            labels[i]: float(probabilities[i].item())
                            for i in range(len(probabilities))
                        }
                    }
                }

                del inputs, outputs, probabilities
                del pil_image, rgb_image

                return result

            else:
                raise ValueError(
                    f"Unsupported image type: {image_type}"
                )

        finally:
            if image_type in {"skin", "oral", "wound"}:
                self._release_model(image_type)

    def analyze(
        self,
        image=None,
        image_type=None,
        symptoms=None,
        patient=None,
        run_symptom_model=True,
        run_patient_model=True
    ):
        with self._inference_lock:
            try:
                return self._analyze_locked(
                    image=image,
                    image_type=image_type,
                    symptoms=symptoms,
                    patient=patient,
                    run_symptom_model=run_symptom_model,
                    run_patient_model=run_patient_model
                )
            finally:
                self._release_all_models()

    def _analyze_locked(
        self,
        image=None,
        image_type=None,
        symptoms=None,
        patient=None,
        run_symptom_model=True,
        run_patient_model=True
    ):
        symptoms = symptoms or {}
        patient = patient or {}

        symptom_result = {}
        patient_result = {}

        if run_symptom_model:
            try:
                symptom_model = self._get_symptom_model()

                symptom_result = symptom_model.predict_text(
                    self._build_symptom_text(symptoms)
                )
            finally:
                self._release_model("symptom")

        if run_patient_model:
            try:
                from ai.patient.features import encode_patient

                patient_features = encode_patient(patient)

                patient_model = self._get_patient_model()

                patient_result = patient_model.predict(
                    np.asarray(
                        patient_features
                    ).reshape(1, -1)
                )
            finally:
                self._release_model("patient")

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
            confidence = (
                image_result["prediction"].get("confidence")
            )
            if confidence is not None:
                confidences.append(float(confidence))

        if symptom_result:
            confidence = symptom_result.get("confidence")
            if confidence is not None:
                confidences.append(float(confidence))

        if patient_result:
            confidence = patient_result.get("confidence")
            if confidence is not None:
                confidences.append(float(confidence))

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

        return (
            ". ".join(parts)
            if parts
            else "No symptoms reported."
        )
