from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


SensoryState = Literal[
    "too_noisy",
    "too_bright",
    "crowded",
    "overwhelmed",
    "need_quiet",
    "need_space",
    "need_break",
]


class SensoryStateCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sensory_state: SensoryState
    intensity: int = Field(ge=1, le=10)
    optional_note: Optional[str] = Field(default=None, max_length=1000)

    @field_validator("optional_note")
    @classmethod
    def normalize_optional_note(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class SensoryStateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str
    user_id: str
    sensory_state: SensoryState
    intensity: int = Field(ge=1, le=10)
    optional_note: Optional[str] = None
    created_at: datetime
    suggestions: List[str] = Field(default_factory=list)
