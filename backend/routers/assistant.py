import logging

from fastapi import APIRouter, Depends, HTTPException

from backend.auth import get_current_user_id
from backend.schemas.assistant import AssistantRequest, AssistantResponse
from backend.services.assistant_service import AssistantService
from backend.services.supabase_service import SupabaseService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/assistant",
    tags=["Assistant"]
)

assistant_service = None
supabase_service = None


def get_assistant_service():
    global assistant_service

    if assistant_service is None:
        assistant_service = AssistantService()

    return assistant_service


def get_supabase_service():
    global supabase_service

    if supabase_service is None:
        supabase_service = SupabaseService()

    return supabase_service


@router.post("/chat", response_model=AssistantResponse)
def chat(
    request: AssistantRequest,
    user_id: str = Depends(get_current_user_id)
):
    try:
        checkup = get_supabase_service().get_checkup_context(
            user_id=user_id,
            checkup_id=request.checkup_id
        )

        if not checkup:
            raise HTTPException(
                status_code=404,
                detail="No checkup result found"
            )

        response = get_assistant_service().chat(
            message=request.message,
            checkup_context=checkup
        )

        return {
            "status": "completed",
            "message": response,
            "context": checkup
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Assistant request failed")

        raise HTTPException(
            status_code=500,
            detail="Assistant request failed"
        )
