import json

import os

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.schemas.checkup import CheckupRequest, CheckupResponse
from backend.services.ai_service import AIService
from backend.services.supabase_service import SupabaseService


router = APIRouter(
    prefix="/api/v1/checkups",
    tags=["Checkups"]
)

ai_service = AIService()
supabase_service = SupabaseService()


@router.post("/analyze", response_model=CheckupResponse)
def analyze_checkup(request: CheckupRequest):
    result = ai_service.analyze(
        symptoms=request.symptoms,
        patient=request.patient
    )

    user_id = os.getenv("SUPABASE_TEST_USER_ID")

    checkup_id = supabase_service.save_checkup(
        user_id=user_id,
        symptoms=request.symptoms,
        patient=request.patient,
        result=result
    )

    return {
        "status": "completed",
        "assessment": {
            "overall": result["fusion_result"]["health_vector"]
        },
        "symptom_result": result["symptom_result"],
        "patient_result": result["patient_result"],
        "fusion_result": result["fusion_result"],
        "uncertainty": result["uncertainty"]
    }


@router.post("/analyze-image", response_model=CheckupResponse)
async def analyze_checkup_with_image(
    symptoms: str = Form(...),
    patient: str = Form(...),
    image_type: str = Form(...),
    image: UploadFile = File(...)
):
    if image_type not in {"skin", "oral", "wound"}:
        raise HTTPException(
            status_code=400,
            detail="image_type must be skin, oral, or wound"
        )

    try:
        symptoms_data = json.loads(symptoms)
        patient_data = json.loads(patient)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="symptoms and patient must be valid JSON strings"
        )

    image_bytes = await image.read()

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image_data = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image_data is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file"
        )

    result = ai_service.analyze(
        symptoms=symptoms_data,
        patient=patient_data,
        image=image_data,
        image_type=image_type
    )

    user_id = os.getenv("SUPABASE_TEST_USER_ID")

    checkup_id = supabase_service.save_checkup(
        user_id=user_id,
        symptoms=symptoms_data,
        patient=patient_data,
        result=result,
        image_bytes=image_bytes,
        image_type=image_type,
        image_name=image.filename,
        image_mime_type=image.content_type
    )

    return {
        "status": "completed",
        "assessment": {
            "overall": result["fusion_result"]["health_vector"]
        },
        "symptom_result": result["symptom_result"],
        "patient_result": result["patient_result"],
        "fusion_result": result["fusion_result"],
        "uncertainty": result["uncertainty"]
    }