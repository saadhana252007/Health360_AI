import os
import uuid

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()


class SupabaseService:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SECRET_KEY")

        if not url or not key:
            raise RuntimeError("Supabase environment variables are missing")

        self.client = create_client(url, key)

    def get_overall_category(self, overall_score):
      if overall_score < 0.33:
        return "LOW"
      elif overall_score < 0.66:
        return "MODERATE"
      return "HIGH"    

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
        fusion = result["fusion_result"]
        uncertainty = result["uncertainty"]

        health_vector = fusion["health_vector"][0]

        overall_score = float(health_vector[-1])
        overall_category = self.get_overall_category(overall_score)

        checkup_response = (
            self.client
            .table("checkups")
            .insert({
                "user_id": user_id,
                "status": "completed",
                "overall_score": overall_score,
                "overall_category": overall_category,
                "confidence": float(fusion["confidence"]),
                "uncertainty": float(uncertainty["uncertainty"]),
                "completeness": float(fusion["completeness"])
            })
            .execute()
        )

        if not checkup_response.data:
            raise RuntimeError("Failed to save checkup")

        checkup_id = checkup_response.data[0]["id"]

        self.client.table("symptoms").insert({
            "checkup_id": checkup_id,
            "symptom_data": symptoms
        }).execute()

        self.client.table("vitals").insert({
            "checkup_id": checkup_id,
            "vitals_data": patient
        }).execute()

        self.client.table("model_results").insert([
            {
                "checkup_id": checkup_id,
                "model_name": result["symptom_result"]["model"],
                "model_version": result["symptom_result"]["version"],
                "modality": "symptoms",
                "result": result["symptom_result"]
            },
            {
                "checkup_id": checkup_id,
                "model_name": result["patient_result"]["model"],
                "model_version": result["patient_result"]["version"],
                "modality": "patient",
                "result": result["patient_result"]
            }
        ]).execute()

        self.client.table("fusion_results").insert({
            "checkup_id": checkup_id,
            "health_vector": fusion["health_vector"],
            "confidence": float(fusion["confidence"]),
            "uncertainty": float(uncertainty["uncertainty"]),
            "completeness": float(fusion["completeness"]),
            "contributors": fusion.get("gates", [])
        }).execute()

        if image_bytes is not None and image_type is not None:
            extension = "jpg"

            if image_name and "." in image_name:
                extension = image_name.rsplit(".", 1)[1].lower()

            file_path = (
                f"{user_id}/{checkup_id}/{image_type}/"
                f"{uuid.uuid4().hex}.{extension}"
            )

            self.client.storage.from_("health-images").upload(
                file=image_bytes,
                path=file_path,
                file_options={
                    "content-type": image_mime_type or "image/jpeg",
                    "upsert": "false"
                }
            )

            self.client.table("image_inputs").insert({
                "checkup_id": checkup_id,
                "image_type": image_type,
                "storage_path": file_path,
                "original_file_name": image_name,
                "mime_type": image_mime_type
            }).execute()

        return checkup_id