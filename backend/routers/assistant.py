
from fastapi import APIRouter, HTTPException

from backend.schemas.assistant import AssistantRequest, AssistantResponse
from backend.services.assistant_service import AssistantService
from backend.services.supabase_service import SupabaseService

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
def chat(request: AssistantRequest):
    try:
        checkup = get_supabase_service().get_checkup_context(
            user_id=request.user_id,
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
        raise HTTPException(
            status_code=500,
            detail="Assistant request failed"
        )
