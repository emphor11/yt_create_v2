from typing import Any
from pydantic import BaseModel, Field


class VisualDirective(BaseModel):
    beat_id: str
    preferred_component: str | None = None
    visual_goal: str | None = None
    visual_instruction: str | None = None  # Backward compatibility field
    onscreen_text: str | None = None
    asset_query: str | None = None
    notes: str | None = None
    trigger_word: str | None = None
    component_data: dict[str, Any] = Field(default_factory=dict)

    def get_visual_instruction(self) -> str:
        return self.visual_instruction or self.visual_goal or ""


class Hook(BaseModel):
    schema_version: str = "1"
    conceptual_hook: str
    script_text: str
    visual_directives: list[VisualDirective] = Field(default_factory=list)

