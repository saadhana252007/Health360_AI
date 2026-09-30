import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SECRET_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_SECRET_KEY must be configured"
            )

        self.client = create_client(
            self.url,
            self.key
        )

    def save_checkup(
        self,
        user_id,
        symptoms,
        patient,
        result,
        image_bytes=None,
        image_type=None,
        image_name=None,
        image_mime_type=None
    ):
        image_result = result.get(
            "image_result"
        )
        symptom_result = result.get(
            "symptom_result",
            {}
        )
        patient_result = result.get(
            "patient_result",
            {}
        )
        fusion_result = result.get(
            "fusion_result",
            {}
        )
        uncertainty = result.get(
            "uncertainty",
            {}
        )
        screening = result.get(
            "screening",
            {}
        )

        confidence = float(
            uncertainty.get(
                "confidence",
                0.0
            )
        )

        uncertainty_value = float(
            uncertainty.get(
                "uncertainty",
                1.0
            )
        )

        completeness = float(
            uncertainty.get(
                "completeness",
                0.0
            )
        )

        overall_category = screening.get(
            "main_concern",
            "AI-assisted assessment"
        )

        record = {
            "user_id": user_id,
            "status": "completed",
            "overall_score": confidence,
            "overall_category": overall_category,
            "confidence": confidence,
            "uncertainty": uncertainty_value,
            "completeness": completeness,
            "symptoms": symptoms,
            "patient_data": patient,
            "image_result": image_result,
            "symptom_result": symptom_result,
            "patient_result": patient_result,
            "fusion_result": fusion_result,
            "screening": result.get("screening"),
            "uncertainty_data": uncertainty,
            "created_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

        response = self.client.table(
            "checkups"
        ).insert(
            record
        ).execute()

        if not response.data:
            raise RuntimeError(
                "Failed to save checkup"
            )

        return response.data[0].get("id")

    def get_checkup_context(
        self,
        user_id,
        checkup_id=None
    ):
        query = self.client.table(
            "checkups"
        ).select(
            "id,user_id,status,overall_category,confidence,uncertainty,completeness,symptoms,patient_data,image_result,symptom_result,patient_result,fusion_result,screening,uncertainty_data,created_at"
        ).eq(
            "user_id",
            user_id
        )

        if checkup_id:
            query = query.eq(
                "id",
                checkup_id
            )
        else:
            query = query.order(
                "created_at",
                desc=True
            ).limit(1)

        response = query.execute()

        if not response.data:
            return None

        return response.data[0]