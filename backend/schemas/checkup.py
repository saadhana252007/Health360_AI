from typing import Any

from pydantic import BaseModel, Field


class CheckupRequest(BaseModel):
    symptoms: dict[str, Any] = Field(default_factory=dict)
    patient: dict[str, Any] = Field(default_factory=dict)


class CheckupResponse(BaseModel):
    status: str
    assessment: dict[str, Any]
    symptom_result: dict[str, Any]
    patient_result: dict[str, Any]
    fusion_result: dict[str, Any]
    uncertainty: dict[str, Any]