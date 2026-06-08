from pydantic import BaseModel, ConfigDict, Field


class SemanticEntity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    role: str
    raw: str
    value: int
    unit: str
    source_text: str


class SemanticRelationship(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    from_entity_id: str
    to_entity_id: str


class SemanticScene(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    primary_concept: str
    confidence: float
    warnings: list[str] = Field(default_factory=list)
    entities: list[SemanticEntity] = Field(default_factory=list)
    relationships: list[SemanticRelationship] = Field(default_factory=list)
