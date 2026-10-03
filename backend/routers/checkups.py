
import json
import os

import cv2
import numpy as np
from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.schemas.checkup import CheckupRequest, CheckupResponse
from backend.services.ai_service import AIService, ModelUnavailableError
from backend.services.supabase_service import SupabaseService


router = APIRouter(
    prefix="/api/v1/checkups",
    tags=["Checkups"],
)

ai_service = None
supabase_service = None


def get_ai_service():
    global ai_service

    if ai_service is None:
        ai_service = AIService()

    return ai_service


def get_supabase_service():
    global supabase_service

    if supabase_service is None:
        supabase_service = SupabaseService()

    return supabase_service


@router.post("/analyze", response_model=CheckupResponse)
def analyze_checkup(request: CheckupRequest):
    try:
        result = get_ai_service().analyze(
            symptoms=request.symptoms,
            patient=request.patient,
        )

        user_id = os.getenv("SUPABASE_TEST_USER_ID")

        if not user_id:
            raise HTTPException(
                status_code=500,
                detail="SUPABASE_TEST_USER_ID is not configured",
            )

        get_supabase_service().save_checkup(
            user_id=user_id,
            symptoms=request.symptoms,
            patient=request.patient,
            result=result,
        )

        return {
            "status": "completed",
            "assessment": {
                "image_type": None,
                "finding": None,
                "confidence": None,
                "probabilities": {},
            },
            "screening": result["screening"],
            "image_result": result["image_result"],
            "symptom_result": result["symptom_result"],
            "patient_result": result["patient_result"],
            "uncertainty": result["uncertainty"],
        }

    except HTTPException:
        raise

    # ADDED: Must come before the generic Exception handler.
    except ModelUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Checkup analysis failed: {str(error)}",
        ) from error


@router.post("/analyze-image", response_model=CheckupResponse)
async def analyze_checkup_with_image(
    user_id: str = Form(...),
    symptoms: str = Form(...),
    patient: str = Form(...),
    image_type: str = Form(...),
    image: UploadFile = File(...),
):
    if image_type not in {"skin", "oral", "wound"}:
        raise HTTPException(
            status_code=400,
            detail="image_type must be skin, oral, or wound",
        )

    try:
        symptoms_data = json.loads(symptoms)
        patient_data = json.loads(patient)
    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=400,
            detail="symptoms and patient must be valid JSON strings",
        ) from error

    image_bytes = await image.read()

    if not image_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded image is empty",
        )

    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image_data = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image_data is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file",
        )

    try:
        result = get_ai_service().analyze(
            symptoms=symptoms_data,
            patient=patient_data,
            image=image_data,
            image_type=image_type,
            run_symptom_model=False,
            run_patient_model=False,
        )

        if not result.get("image_result"):
            raise HTTPException(
                status_code=500,
                detail="Image analysis did not return a result",
            )

        prediction = result["image_result"]["prediction"]

        get_supabase_service().save_checkup(
            user_id=user_id,
            symptoms=symptoms_data,
            patient=patient_data,
            result=result,
            image_bytes=image_bytes,
            image_type=image_type,
            image_name=image.filename,
            image_mime_type=image.content_type,
        )

        return {
            "status": "completed",
            "assessment": {
                "image_type": image_type,
                "finding": prediction.get("class_name"),
                "confidence": prediction.get("confidence"),
                "probabilities": prediction.get("probabilities", {}),
            },
            "screening": result["screening"],
            "image_result": result["image_result"],
            "symptom_result": result["symptom_result"],
            "patient_result": result["patient_result"],
            "uncertainty": result["uncertainty"],
        }

    except HTTPException:
        raise

    # ADDED: This catches a disabled wound model and returns HTTP 503.
    except ModelUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(error)}",
        ) from error
