class MultimodalFusion:

    def __init__(self):
        self.version = "fusion_v3"

    def fuse(
        self,
        image_result=None,
        symptom_result=None,
        patient_result=None,
        patient=None
    ):
        image_result = image_result or {}
        symptom_result = symptom_result or {}
        patient_result = patient_result or {}
        patient = patient or {}

        evidence = []

        image_prediction = image_result.get("prediction")
        symptom_class = symptom_result.get("class_name")
        patient_class = patient_result.get("class_name")

        if image_prediction:
            evidence.append({
                "source": image_result.get("type", "image"),
                "finding": image_prediction.get("class_name"),
                "confidence": float(
                    image_prediction.get("confidence", 0.0)
                )
            })

        if symptom_result:
            evidence.append({
                "source": "symptoms",
                "finding": symptom_class,
                "confidence": float(
                    symptom_result.get("confidence", 0.0)
                )
            })

        if patient_result:
            evidence.append({
                "source": "patient_risk",
                "finding": patient_class,
                "confidence": float(
                    patient_result.get("confidence", 0.0)
                )
            })

        vital_analysis = self._analyze_vitals(patient)

        if vital_analysis["available"]:
            evidence.append({
                "source": "vitals",
                "finding": vital_analysis["summary"],
                "confidence": vital_analysis["confidence"]
            })

        confidences = []

        if image_prediction:
            confidences.append(
                float(
                    image_prediction.get(
                        "confidence",
                        0.0
                    )
                )
            )

        if symptom_result:
            confidences.append(
                float(
                    symptom_result.get(
                        "confidence",
                        0.0
                    )
                )
            )

        if patient_result:
            confidences.append(
                float(
                    patient_result.get(
                        "confidence",
                        0.0
                    )
                )
            )

        if vital_analysis["available"]:
            confidences.append(
                vital_analysis["confidence"]
            )

        overall_confidence = (
            sum(confidences) / len(confidences)
            if confidences
            else 0.0
        )

        overall_status = self._determine_status(
            symptom_result,
            vital_analysis
        )

        return {
            "model": self.version,
            "available_modalities": len(evidence),
            "evidence": evidence,
            "overall_confidence": overall_confidence,
            "overall_status": overall_status,
            "vital_analysis": vital_analysis,
            "interpretation": self._build_interpretation(
                overall_status,
                symptom_class,
                vital_analysis
            )
        }

    def _analyze_vitals(self, patient):

        findings = []
        invalid = []
        abnormal = []

        heart_rate = self._number(
            patient.get("heart_rate")
        )

        systolic = self._number(
            patient.get("systolic_bp")
        )

        diastolic = self._number(
            patient.get("diastolic_bp")
        )

        spo2 = self._number(
            patient.get("spo2")
        )

        temperature = self._number(
            patient.get("temperature")
        )

        available = any(
            value is not None
            for value in [
                heart_rate,
                systolic,
                diastolic,
                spo2,
                temperature
            ]
        )

        if heart_rate is not None:

            if heart_rate < 30 or heart_rate > 220:
                invalid.append(
                    f"Heart rate {heart_rate:.0f} bpm is outside the supported measurement range."
                )

            elif heart_rate < 60:
                abnormal.append(
                    f"Heart rate is low at {heart_rate:.0f} bpm."
                )

            elif heart_rate > 100:
                abnormal.append(
                    f"Heart rate is elevated at {heart_rate:.0f} bpm."
                )

            else:
                findings.append(
                    f"Heart rate {heart_rate:.0f} bpm is within the typical resting adult range."
                )

        if systolic is not None and diastolic is not None:

            if (
                systolic < 60
                or systolic > 300
                or diastolic < 30
                or diastolic > 200
                or systolic <= diastolic
            ):
                invalid.append(
                    f"Blood pressure {systolic:.0f}/{diastolic:.0f} mmHg is not a valid blood pressure reading."
                )

            elif systolic > 180 or diastolic > 120:
                abnormal.append(
                    f"Blood pressure is in the severe range at {systolic:.0f}/{diastolic:.0f} mmHg."
                )

            elif systolic >= 140 or diastolic >= 90:
                abnormal.append(
                    f"Blood pressure is high at {systolic:.0f}/{diastolic:.0f} mmHg."
                )

            elif systolic >= 130 or diastolic >= 80:
                abnormal.append(
                    f"Blood pressure is above the normal range at {systolic:.0f}/{diastolic:.0f} mmHg."
                )

            else:
                findings.append(
                    f"Blood pressure {systolic:.0f}/{diastolic:.0f} mmHg is not elevated."
                )

        if spo2 is not None:

            if spo2 < 50 or spo2 > 100:
                invalid.append(
                    f"SpO₂ of {spo2:.0f}% is outside the valid 0–100% range. Please remeasure."
                )

            elif spo2 < 90:
                abnormal.append(
                    f"SpO₂ is low at {spo2:.0f}%."
                )

            elif spo2 < 95:
                abnormal.append(
                    f"SpO₂ is below the typical range at {spo2:.0f}%."
                )

            else:
                findings.append(
                    f"SpO₂ of {spo2:.0f}% is within the typical range."
                )

        if temperature is not None:

            if temperature < 25 or temperature > 45:
                invalid.append(
                    f"Temperature of {temperature:.1f}°C is outside a plausible body-temperature range. Please check whether the unit or value is correct."
                )

            elif temperature >= 38:
                abnormal.append(
                    f"Temperature is elevated at {temperature:.1f}°C."
                )

            elif temperature < 35:
                abnormal.append(
                    f"Temperature is low at {temperature:.1f}°C."
                )

            else:
                findings.append(
                    f"Temperature of {temperature:.1f}°C is not elevated."
                )

        abnormal_count = len(abnormal)
        invalid_count = len(invalid)

        if invalid_count > 0:
            confidence = 0.2
        elif abnormal_count == 0:
            confidence = 0.9
        elif abnormal_count == 1:
            confidence = 0.7
        else:
            confidence = 0.5

        if invalid:
            summary = "Invalid vital measurement(s) detected."
        elif abnormal:
            summary = "Abnormal vital measurement(s) detected."
        else:
            summary = "No abnormal vital measurements detected."

        return {
            "available": available,
            "findings": findings,
            "abnormal": abnormal,
            "invalid": invalid,
            "abnormal_count": abnormal_count,
            "invalid_count": invalid_count,
            "confidence": confidence,
            "summary": summary
        }

    def _determine_status(
        self,
        symptom_result,
        vital_analysis
    ):

        if vital_analysis["invalid_count"] > 0:
            return "INPUT_RECHECK_REQUIRED"

        if (
            vital_analysis["abnormal_count"] >= 2
        ):
            return "MEDICAL_REVIEW_RECOMMENDED"

        if (
            vital_analysis["abnormal_count"] == 1
        ):
            symptom_class = symptom_result.get(
                "class_name",
                ""
            )

            if symptom_class == "urgent":
                return "URGENT_ATTENTION"

            if symptom_class == "consult_gp":
                return "MEDICAL_REVIEW_RECOMMENDED"

            return "ATTENTION_REQUIRED"

        symptom_class = symptom_result.get(
            "class_name",
            ""
        )

        if symptom_class == "urgent":
            return "URGENT_ATTENTION"

        if symptom_class == "consult_gp":
            return "MEDICAL_REVIEW_RECOMMENDED"

        return "MONITOR"

    def _build_interpretation(
        self,
        status,
        symptom_class,
        vital_analysis
    ):

        if status == "INPUT_RECHECK_REQUIRED":
            return (
                "The screening cannot be reliably interpreted until the invalid "
                "vital measurements are corrected and rechecked."
            )

        if status == "URGENT_ATTENTION":
            return (
                "The combined screening identified information that requires "
                "prompt medical attention."
            )

        if status == "MEDICAL_REVIEW_RECOMMENDED":
            return (
                "The combined screening identified more than one finding that "
                "should be reviewed with a healthcare professional."
            )

        if status == "ATTENTION_REQUIRED":
            return (
                "The combined screening identified an abnormal finding that "
                "should be rechecked and monitored."
            )

        return (
            "The available symptom, vital and patient-risk information does not "
            "show an immediate high-risk pattern in this screening."
        )

    def _number(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None