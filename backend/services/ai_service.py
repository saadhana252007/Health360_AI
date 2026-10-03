
import gc
import logging
import os
import threading

import cv2
import numpy as np

from backend.services.interpretation_service import InterpretationService


logger = logging.getLogger("health360.memory")


def log_memory(stage: str) -> None:
    """Log process RAM usage in MB."""
    try:
        import psutil

        rss_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
        logger.warning("MEMORY_CHECK stage=%s rss_mb=%.1f", stage, rss_mb)
    except Exception:
        logger.exception("Unable to record memory usage at stage=%s", stage)


class ModelUnavailableError(RuntimeError):
    """Raised when a model is disabled for the current deployment."""


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

        # Do not run concurrent model inference in the same process.
        self._inference_lock = threading.Lock()
        self.interpretation_service = InterpretationService()

    @staticmethod
    def _enabled(variable_name: str, default: bool = False) -> bool:
        value = os.getenv(variable_name, str(default)).strip().lower()
        return value in {"1", "true", "yes", "on"}

    def _get_skin_model(self):
        if self._skin_model is None:
            log_memory("before_skin_load")
            from ai.vision.skin.model import SkinModel

            self._skin_model = SkinModel(num_classes=5, pretrained=False)
            self._skin_model.eval()
            log_memory("after_skin_load")
        return self._skin_model

    def _get_oral_model(self):
        if self._oral_model is None:
            log_memory("before_oral_load")
            from ai.vision.oral.model import OralModel

            self._oral_model = OralModel(num_classes=6, pretrained=False)
            self._oral_model.eval()
            log_memory("after_oral_load")
        return self._oral_model

    def _get_wound_model(self):
        if not self._enabled("ENABLE_LOCAL_WOUND_MODEL", False):
            raise ModelUnavailableError(
                "Wound image analysis is disabled on this low-memory deployment."
            )

        if self._wound_model is None:
            log_memory("before_wound_load")
            from transformers import (
                AutoImageProcessor,
                AutoModelForImageClassification,
            )

            model_name = "Hemgg/wound-image-classification"

            self._wound_processor = AutoImageProcessor.from_pretrained(model_name)
            self._wound_model = AutoModelForImageClassification.from_pretrained(
                model_name,
                low_cpu_mem_usage=True,
            )
            self._wound_model.to(self.device)
            self._wound_model.eval()
            log_memory("after_wound_load")

        return self._wound_model

    def _get_symptom_model(self):
        if not self._enabled("ENABLE_LOCAL_SYMPTOM_MODEL", False):
            raise ModelUnavailableError(
                "The local symptom Transformer is disabled on this low-memory deployment."
            )

        if self._symptom_model is None:
            log_memory("before_symptom_load")
            from ai.symptoms.model import SymptomModel

            self._symptom_model = SymptomModel()
            log_memory("after_symptom_load")

        return self._symptom_model

    def _get_patient_model(self):
        if self._patient_model is None:
            log_memory("before_patient_load")
            from ai.patient.model import PatientRiskModel

            self._patient_model = PatientRiskModel()
            log_memory("after_patient_load")
        return self._patient_model

    def _get_fusion_model(self):
        if self._fusion_model is None:
            from ai.fusion.model import MultimodalFusion

            self._fusion_model = MultimodalFusion()
        return self._fusion_model

    def _release_model(self, model_type: str) -> None:
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
        log_memory(f"after_release_{model_type}")

    def _release_all_models(self) -> None:
        self._skin_model = None
        self._oral_model = None
        self._wound_processor = None
        self._wound_model = None
        self._symptom_model = None
        self._patient_model = None

        # Keep only the lightweight fusion model cached.
        gc.collect()
        log_memory("after_release_all_models")

    def _run_symptom_model(self, symptoms):
        """Separate frame ensures the local Transformer reference can be released."""
        try:
            model = self._get_symptom_model()
            result = model.predict_text(self._build_symptom_text(symptoms))
            log_memory("after_symptom_inference")
            return result
        finally:
            self._release_model("symptom")

    def _run_patient_model(self, patient):
        """Run the patient-risk model separately from other model objects."""
        try:
            from ai.patient.features import encode_patient

            model = self._get_patient_model()
            features = encode_patient(patient)
            result = model.predict(np.asarray(features).reshape(1, -1))
            log_memory("after_patient_inference")
            return result
        finally:
            self._release_model("patient")

    def _analyze_image(self, image, image_type):
        import torch
        from PIL import Image

        from ai.common.preprocessing import (
            get_inference_transform,
            preprocess_image,
        )

        try:
            log_memory(f"before_{image_type}_inference")

            if image_type in {"skin", "oral"}:
                tensor = preprocess_image(image, get_inference_transform())

                if image_type == "skin":
                    model = self._get_skin_model()
                else:
                    model = self._get_oral_model()

                with torch.inference_mode():
                    prediction = model.predict(tensor)

                result = {
                    "type": image_type,
                    "status": "completed",
                    "prediction": prediction,
                }

                del tensor
                log_memory(f"after_{image_type}_inference")
                return result

            if image_type == "wound":
                model = self._get_wound_model()
                processor = self._wound_processor

                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(rgb_image)
                inputs = processor(images=pil_image, return_tensors="pt")

                with torch.inference_mode():
                    outputs = model(**inputs)
                    probabilities = torch.softmax(outputs.logits, dim=1)[0]
                    index = int(torch.argmax(probabilities).item())

                    labels = model.config.id2label
                    prediction = {
                        "class_index": index,
                        "class_name": labels.get(index, str(index)),
                        "confidence": float(probabilities[index].item()),
                        "probabilities": {
                            labels.get(i, str(i)): float(probabilities[i].item())
                            for i in range(len(probabilities))
                        },
                    }

                del inputs, outputs, probabilities, pil_image, rgb_image
                log_memory("after_wound_inference")

                return {
                    "type": "wound",
                    "status": "completed",
                    "prediction": prediction,
                }

            raise ValueError(f"Unsupported image type: {image_type}")

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
        run_patient_model=True,
    ):
        with self._inference_lock:
            log_memory("analysis_start")
            try:
                return self._analyze_locked(
                    image=image,
                    image_type=image_type,
                    symptoms=symptoms,
                    patient=patient,
                    run_symptom_model=run_symptom_model,
                    run_patient_model=run_patient_model,
                )
            finally:
                self._release_all_models()
                log_memory("analysis_end")

    def _analyze_locked(
        self,
        image=None,
        image_type=None,
        symptoms=None,
        patient=None,
        run_symptom_model=True,
        run_patient_model=True,
    ):
        symptoms = symptoms or {}
        patient = patient or {}

        symptom_result = {
            "status": "not_run",
            "reason": "Symptom model was not requested.",
        }
        patient_result = {
            "status": "not_run",
            "reason": "Patient risk model was not requested.",
        }

        if run_symptom_model:
            if self._enabled("ENABLE_LOCAL_SYMPTOM_MODEL", False):
                symptom_result = self._run_symptom_model(symptoms)
                if isinstance(symptom_result, dict):
                    symptom_result.setdefault("status", "completed")
            else:
                symptom_result = {
                    "status": "unavailable",
                    "reason": (
                        "Local symptom Transformer is disabled to reduce RAM "
                        "usage on this deployment."
                    ),
                }

        if run_patient_model:
            try:
                patient_result = self._run_patient_model(patient)
                if isinstance(patient_result, dict):
                    patient_result.setdefault("status", "completed")
            except Exception:
                logger.exception("Patient-risk inference failed")
                patient_result = {
                    "status": "error",
                    "reason": "Patient-risk inference failed.",
                }

        image_result = None
        if image is not None and image_type is not None:
            image_result = self._analyze_image(image, image_type)

        # Do not send placeholder dictionaries as model predictions.
        fusion_symptom_result = (
            symptom_result
            if symptom_result.get("status") == "completed"
            else {}
        )
        fusion_patient_result = (
            patient_result
            if patient_result.get("status") == "completed"
            else {}
        )

        fusion_result = self._get_fusion_model().fuse(
            image_result=image_result,
            symptom_result=fusion_symptom_result,
            patient_result=fusion_patient_result,
            patient=patient,
        )

        confidences = []

        if image_result and image_result.get("status") == "completed":
            confidence = image_result.get("prediction", {}).get("confidence")
            if confidence is not None:
                confidences.append(float(confidence))

        if fusion_symptom_result:
            confidence = fusion_symptom_result.get("confidence")
            if confidence is not None:
                confidences.append(float(confidence))

        if fusion_patient_result:
            confidence = fusion_patient_result.get("confidence")
            if confidence is not None:
                confidences.append(float(confidence))

        overall_confidence = (
            sum(confidences) / len(confidences) if confidences else 0.0
        )

        uncertainty = {
            "confidence": overall_confidence,
            "uncertainty": 1.0 - overall_confidence,
            "completeness": self._calculate_completeness(symptoms, patient),
            "image_quality": 1.0 if image is not None else None,
        }

        screening = self.interpretation_service.interpret(
            symptoms=symptoms,
            patient=patient,
            symptom_result=fusion_symptom_result,
            patient_result=fusion_patient_result,
            image_result=image_result,
            fusion_result=fusion_result,
            uncertainty=uncertainty,
        )

        return {
            "image_result": image_result,
            "symptom_result": symptom_result,
            "patient_result": patient_result,
            "fusion_result": fusion_result,
            "uncertainty": uncertainty,
            "screening": screening,
            "model_availability": {
                "image": (
                    image_result.get("status", "completed")
                    if image_result
                    else "not_requested"
                ),
                "symptoms": symptom_result.get("status", "unknown"),
                "patient_risk": patient_result.get("status", "unknown"),
            },
        }

    def _calculate_completeness(self, symptoms, patient):
        required_sections = 3
        completed_sections = 0

        profile_fields = [
            "full_name",
            "date_of_birth",
            "sex",
            "height_cm",
            "weight_kg",
        ]
        vital_fields = [
            "heart_rate",
            "systolic_bp",
            "diastolic_bp",
            "spo2",
            "temperature",
        ]

        has_profile = any(
            patient.get(field) not in [None, ""] for field in profile_fields
        )
        has_vitals = any(
            patient.get(field) not in [None, ""] for field in vital_fields
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

        parts = [
            f"{key}: {value}"
            for key, value in symptoms.items()
            if value is not None and str(value).strip()
        ]
        return ". ".join(parts) if parts else "No symptoms reported."
