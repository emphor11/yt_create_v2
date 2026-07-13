from pydantic import BaseModel, Field


class ValidationCheck(BaseModel):
    name: str
    status: str  # "passed", "failed"
    message: str


class ReviewResult(BaseModel):
    schema_version: str = "1"
    approved: bool
    checks: list[ValidationCheck] = Field(default_factory=list)
    feedback: str | None = None
