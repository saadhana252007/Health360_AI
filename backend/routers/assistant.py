from fastapi import APIRouter, HTTPException

from backend.schemas.assistant import AssistantRequest, AssistantResponse
from backend.services.assistant_service import AssistantService
from backend.services.supabase_service import SupabaseService

router = APIRouter(
    prefix="/api/v1/assistant",
    tags=["Assistant"]
)

assistant_service = AssistantService()
supabase_service = SupabaseService()


@router.post("/chat", response_model=AssistantResponse)
def chat(request: AssistantRequest):
    try:
        checkup = supabase_service.get_checkup_context(
            user_id=request.user_id,
            checkup_id=request.checkup_id
        )

        if not checkup:
            raise HTTPException(
                status_code=404,
                detail="No checkup result found"
            )

        response = assistant_service.chat(
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

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )