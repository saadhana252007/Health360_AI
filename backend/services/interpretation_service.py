class InterpretationService:

    def interpret(
        self,
        symptoms,
        patient,
        symptom_result,
        patient_result,
        image_result,
        fusion_result,
        uncertainty
    ):
        symptoms = symptoms or {}
        patient = patient or {}
        symptom_result = symptom_result or {}
        patient_result = patient_result or {}
        image_result = image_result or {}
        fusion_result = fusion_result or {}
        uncertainty = uncertainty or {}

        main_concern = self._get_main_concern(symptoms)

        red_flags = self._detect_red_flags(
            symptoms,
            patient
        )

        vital_analysis = fusion_result.get(
            "vital_analysis",
            {}
        )

        overall_status = fusion_result.get(
            "overall_status",
            "MONITOR"
        )

        if red_flags:
            overall_status = "URGENT_ATTENTION"

        screening_summary = self._build_screening_summary(
            main_concern,
            overall_status,
            red_flags,
            vital_analysis
        )

        triage = self._build_triage(
            overall_status,
            symptom_result
        )

        symptom_explanation = self._build_symptom_explanation(
            main_concern,
            symptom_result
        )

        patient_explanation = self._build_patient_explanation(
            patient_result
        )

        vital_explanation = self._build_vital_explanation(
            vital_analysis
        )

        image_explanation = self._build_image_explanation(
            image_result
        )

        fusion_explanation = self._build_fusion_explanation(
            fusion_result
        )

        next_steps = self._build_next_steps(
            main_concern,
            overall_status,
            red_flags,
            vital_analysis
        )

        explanations = [
            symptom_explanation,
            vital_explanation,
            patient_explanation,
            fusion_explanation
        ]

        if image_explanation:
            explanations.append(
                image_explanation
            )

        return {
            "main_concern": main_concern,
            "overall_status": overall_status,
            "screening_summary": screening_summary,
            "triage": triage,
            "red_flags": red_flags,
            "vitals_interpretation": vital_explanation,
            "model_explanations": explanations,
            "next_steps": next_steps,
            "overall_explanation": self._build_overall_explanation(
                main_concern,
                overall_status,
                symptom_result,
                patient_result,
                image_result,
                vital_analysis
            )
        }

    def _get_main_concern(self, symptoms):
        site = str(
            symptoms.get("site", "")
        ).lower()

        if site in {"head", "1", "1.0"}:
            return "Headache"

        if "head" in site:
            return "Headache"

        if site in {"chest", "2", "2.0"}:
            return "Chest-related symptoms"

        if site in {"abdomen", "3", "3.0"}:
            return "Abdominal symptoms"

        if site in {"back", "4", "4.0"}:
            return "Back-related symptoms"

        if site in {"arms", "5", "5.0"}:
            return "Arm-related symptoms"

        if site in {"legs", "6", "6.0"}:
            return "Leg-related symptoms"

        return "Reported symptoms"

    def _detect_red_flags(
        self,
        symptoms,
        patient
    ):
        text = self._flatten(symptoms).lower()

        flags = []

        if self._contains(
            text,
            "seizure"
        ):
            flags.append(
                "Seizure reported."
            )

        if (
            self._contains(text, "weakness")
            or self._contains(text, "numbness")
        ):
            flags.append(
                "Weakness or numbness reported."
            )

        if (
            self._contains(text, "difficulty speaking")
            or self._contains(text, "speech difficulty")
        ):
            flags.append(
                "Speech difficulty reported."
            )

        if (
            self._contains(text, "vision loss")
            or self._contains(text, "loss of vision")
        ):
            flags.append(
                "Vision loss reported."
            )

        if self._contains(
            text,
            "confusion"
        ):
            flags.append(
                "Confusion reported."
            )

        if (
            self._contains(text, "head injury")
            or self._contains(text, "injury")
        ):
            flags.append(
                "Head injury associated with the symptom."
            )

        if self._contains(
            text,
            "vomiting"
        ):
            flags.append(
                "Vomiting reported."
            )

        if self._contains(
            text,
            "stiff neck"
        ):
            flags.append(
                "Stiff neck reported."
            )

        site = str(
            symptoms.get("site", "")
        ).lower()

        severity = self._safe_float(
            symptoms.get("severity")
        )

        progression = self._safe_float(
            symptoms.get("progression")
        )

        if (
            site in {"head", "1", "1.0"}
            and severity is not None
            and severity >= 9
        ):
            flags.append(
                "Very severe headache reported."
            )

        if (
            site in {"head", "1", "1.0"}
            and severity is not None
            and severity >= 9
            and progression == 2
        ):
            flags.append(
                "Severe headache with worsening progression reported."
            )

        return flags

    def _safe_float(
        self,
        value
    ):
        try:
            return float(value)
        except (
            TypeError,
            ValueError
        ):
            return None

    def _build_screening_summary(
        self,
        main_concern,
        overall_status,
        red_flags,
        vital_analysis
    ):

        if red_flags:
            return (
                f"Warning signs were identified alongside the reported "
                f"{main_concern.lower()}. The combined screening recommends "
                "prompt medical evaluation."
            )

        if overall_status == "INPUT_RECHECK_REQUIRED":
            return (
                "The screening cannot be interpreted reliably because one or "
                "more vital measurements appear invalid. Recheck the measurements "
                "before relying on the screening result."
            )

        if overall_status == "MEDICAL_REVIEW_RECOMMENDED":
            return (
                f"The combined screening found the reported "
                f"{main_concern.lower()} together with multiple abnormal "
                "measurements. Medical review is recommended."
            )

        if overall_status == "ATTENTION_REQUIRED":
            return (
                f"The combined screening found an abnormal measurement "
                f"alongside the reported {main_concern.lower()}. "
                "The measurement should be rechecked and monitored."
            )

        if overall_status == "URGENT_ATTENTION":
            return (
                "The combined screening identified information requiring "
                "prompt medical attention."
            )

        return (
            f"The combined screening did not identify an immediate high-risk "
            f"pattern from the available information for {main_concern.lower()}."
        )

    def _build_triage(
        self,
        overall_status,
        symptom_result
    ):

        if overall_status == "INPUT_RECHECK_REQUIRED":
            return (
                "Please recheck the entered vital measurements before "
                "interpreting this screening."
            )

        if overall_status == "URGENT_ATTENTION":
            return (
                "Prompt medical attention may be appropriate based on the "
                "combined screening findings."
            )

        if overall_status == "MEDICAL_REVIEW_RECOMMENDED":
            return (
                "A healthcare professional should review the combined findings, "
                "especially if the symptoms persist or worsen."
            )

        if overall_status == "ATTENTION_REQUIRED":
            return (
                "Recheck the abnormal measurement and monitor your symptoms."
            )

        class_name = symptom_result.get(
            "class_name",
            ""
        )

        if class_name == "consult_gp":
            return (
                "Consider consulting a healthcare professional if the symptom "
                "persists, worsens or recurs."
            )

        return (
            "No immediate high-risk pattern was identified. Continue monitoring "
            "your symptoms."
        )

    def _build_symptom_explanation(
        self,
        main_concern,
        symptom_result
    ):
        class_name = symptom_result.get(
            "class_name",
            "unknown"
        )

        confidence = float(
            symptom_result.get(
                "confidence",
                0.0
            )
        ) * 100

        label = class_name.replace(
            "_",
            " "
        ).title()

        return (
            f"Symptom model: {label} with {confidence:.1f}% model confidence. "
            f"The model evaluated the reported {main_concern.lower()} pattern. "
            "This classification does not establish the underlying cause."
        )

    def _build_patient_explanation(
        self,
        patient_result
    ):
        class_name = patient_result.get(
            "class_name",
            "No result"
        )

        confidence = float(
            patient_result.get(
                "confidence",
                0.0
            )
        ) * 100

        return (
            f"Patient-risk model: {class_name} with {confidence:.1f}% model "
            "confidence. This is a separate cardiovascular-risk assessment "
            "and is not the diagnosis or cause of the reported symptom."
        )

    def _build_vital_explanation(
        self,
        vital_analysis
    ):
        findings = []

        findings.extend(
            vital_analysis.get(
                "findings",
                []
            )
        )

        findings.extend(
            vital_analysis.get(
                "abnormal",
                []
            )
        )

        findings.extend(
            vital_analysis.get(
                "invalid",
                []
            )
        )

        if not findings:
            return (
                "No usable vital-sign information was available for interpretation."
            )

        return (
            "Vital-sign analysis: "
            + " ".join(findings)
        )

    def _build_image_explanation(
        self,
        image_result
    ):
        if not image_result:
            return None

        prediction = image_result.get(
            "prediction"
        ) or {}

        class_name = prediction.get(
            "class_name"
        )

        confidence = prediction.get(
            "confidence"
        )

        if not class_name:
            return (
                "The image model was run but did not produce a usable classification."
            )

        if confidence is None:
            return (
                f"The {image_result.get('type', 'image')} model produced "
                f"the finding {class_name}."
            )

        return (
            f"The {image_result.get('type', 'image')} model classified the "
            f"image as {class_name} with {float(confidence) * 100:.1f}% "
            "model confidence. This should not be treated as a diagnosis."
        )

    def _build_fusion_explanation(
        self,
        fusion_result
    ):
        modalities = fusion_result.get(
            "available_modalities",
            0
        )

        status = fusion_result.get(
            "overall_status",
            "MONITOR"
        )

        return (
            f"Fusion layer: combined {modalities} available evidence sources "
            f"and produced the cumulative screening status "
            f"{status.replace('_', ' ').lower()}."
        )

    def _build_overall_explanation(
        self,
        main_concern,
        overall_status,
        symptom_result,
        patient_result,
        image_result,
        vital_analysis
    ):
        pieces = []

        pieces.append(
            f"The screening started with the reported {main_concern.lower()}."
        )

        if vital_analysis.get("abnormal"):
            pieces.append(
                "The vital-sign abnormalities were incorporated into the "
                "cumulative assessment rather than being displayed separately."
            )

        if vital_analysis.get("invalid"):
            pieces.append(
                "Some vital measurements were rejected as invalid, so they "
                "were not treated as evidence of good health."
            )

        if patient_result:
            pieces.append(
                "The patient-risk model contributed cardiovascular-risk evidence."
            )

        if image_result:
            pieces.append(
                "The image model contributed image-based evidence."
            )

        pieces.append(
            f"The final screening status is "
            f"{overall_status.replace('_', ' ').lower()}."
        )

        return " ".join(pieces)

    def _build_next_steps(
        self,
        main_concern,
        overall_status,
        red_flags,
        vital_analysis
    ):

        if red_flags:
            return (
                "Seek prompt medical evaluation because warning signs were "
                "identified. Do not rely on this application to determine the cause."
            )

        if overall_status == "INPUT_RECHECK_REQUIRED":
            return (
                "Recheck the vital measurements using the correct units and "
                "a reliable device. Do not interpret the current screening "
                "until the measurements are corrected."
            )

        if overall_status == "MEDICAL_REVIEW_RECOMMENDED":
            return (
                "Recheck the abnormal vital measurements and consider medical "
                "review, especially if the headache persists, worsens, or "
                "additional symptoms appear."
            )

        if overall_status == "ATTENTION_REQUIRED":
            return (
                "Repeat the abnormal measurement and monitor the symptom. "
                "Seek medical advice if the abnormal reading persists or the "
                "symptom worsens."
            )

        return (
            "Monitor the symptom, stay hydrated, maintain regular meals and "
            "rest, and note possible triggers. Seek medical advice if the "
            "symptom persists, worsens, or new warning signs appear."
        )

    def _flatten(self, value):
        if value is None:
            return ""

        if isinstance(value, dict):
            return " ".join(
                self._flatten(v)
                for v in value.values()
            )

        if isinstance(value, list):
            return " ".join(
                self._flatten(v)
                for v in value
            )

        return str(value)

    def _contains(
        self,
        text,
        feature
    ):
        negative = [
            f"no {feature}",
            f"without {feature}",
            f"denies {feature}"
        ]

        if any(
            item in text
            for item in negative
        ):
            return False

        return feature in text