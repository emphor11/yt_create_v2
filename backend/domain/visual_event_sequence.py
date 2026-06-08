from pydantic import BaseModel, ConfigDict, Field


class VisualEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str
    primitive: str
    intent: str
    world_object: str
    semantic_entity_id: str | None = None
    semantic_relationship_type: str | None = None


class VisualEventSequence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    primary_concept: str
    events: list[VisualEvent] = Field(default_factory=list)
