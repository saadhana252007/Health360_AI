from typing import Any
from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    # Ignored by the server: the user is taken from the login token.
    # Kept optional so older app versions that still send it keep working.
    user_id: str | None = None
    message: str
    checkup_id: str | None = None


class AssistantResponse(BaseModel):
    status: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
