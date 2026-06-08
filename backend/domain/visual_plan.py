from pydantic import BaseModel, ConfigDict


class VisualPlanSide(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: str
    semantic_entity_id: str
    label: str
    raw: str
    value: int
    unit: str


class SplitComparisonProps(BaseModel):
    model_config = ConfigDict(extra="forbid")

    left: VisualPlanSide
    right: VisualPlanSide
    attention_shift_event_id: str


class VisualPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    scene_id: str
    primary_concept: str
    component: str
    selection_reason: str
    props: SplitComparisonProps
