from typing import Any
from pydantic import BaseModel, Field

class CheckupRequest(BaseModel):
    user_id: str
    symptoms: dict[str, Any] = Field(default_factory=dict)
    patient: dict[str, Any] = Field(default_factory=dict)

class ScreeningInterpretation(BaseModel):
    main_concern: str
    screening_summary: str
    triage: str
    red_flags: list[str] = Field(default_factory=list)
    vitals_interpretation: str
    model_explanations: list[str] = Field(default_factory=list)
    next_steps: str
    overall_explanation: str

class CheckupResponse(BaseModel):
    status: str
    assessment: dict[str, Any]
    screening: ScreeningInterpretation
    image_result: dict[str, Any] | None = None
    symptom_result: dict[str, Any]
    patient_result: dict[str, Any]
    uncertainty: dict[str, Any]