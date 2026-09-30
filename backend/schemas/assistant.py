from typing import Any
from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    user_id: str
    message: str
    checkup_id: str | None = None


class AssistantResponse(BaseModel):
    status: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)