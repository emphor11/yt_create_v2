from pydantic import BaseModel, Field


class VisualDirective(BaseModel):
    beat_id: str
    visual_instruction: str
    onscreen_text: str | None = None


class Hook(BaseModel):
    schema_version: str = "1"
    conceptual_hook: str
    script_text: str
    visual_directives: list[VisualDirective] = Field(default_factory=list)
