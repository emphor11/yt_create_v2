"""
Visual Intent domain models.

A VisualIntent represents what the viewer must understand from a segment of narration —
expressed semantically, without any reference to rendering components or layout.

The LLM's job is to group narration sentences into meaningful intents and classify
each intent using the closed relationship_type set.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


# Closed set of semantic relationship types.
# The LLM must choose one of these for every VisualIntent.
# This drives deterministic composition selection — no open-ended LLM invention.
VALID_RELATIONSHIP_TYPES: list[str] = [
    "metric",         # A single important number/value the viewer must register
    "calculation",    # input + operation → result (math story)
    "cause_effect",   # A causes/leads to B
    "multi_factor",   # multiple independent causes → combined outcome/pressure
    "comparison",     # A vs B side-by-side
    "trend",          # a value changes over time (direction unspecified)
    "decline",        # a value specifically decreases over time
    "ranking",        # ordered list by magnitude or priority
    "process",        # sequential steps in a procedure
    "statement",      # key claim or thesis — no data needed
    "quote",          # attributed quote from a person
    "definition",     # explain what X is / means
    "broll",          # atmospheric/contextual moment — no infographic appropriate
]


class VisualIntent(BaseModel):
    """
    A single semantic visual intent derived from one or more narration sentences.

    Multiple sentences that together express one viewer understanding should produce
    a single VisualIntent. Filler or transitional sentences produce no VisualIntent.
    """

    intent_id: str = Field(
        description="Sequential identifier: intent_01, intent_02, ..."
    )
    narration_excerpt: str = Field(
        description="Verbatim narration sentences this intent covers."
    )
    what_viewer_must_understand: str = Field(
        description="One sentence describing what the viewer must understand after seeing this visual."
    )
    key_values: list[str] = Field(
        default_factory=list,
        description="Explicit values or quantities mentioned, e.g. '₹50 lakh', '4%', '15 years'.",
    )
    relationship_type: str = Field(
        description=f"Semantic relationship type. Must be one of: {', '.join(VALID_RELATIONSHIP_TYPES)}",
    )
    emphasis: str | None = Field(
        default=None,
        description=(
            "Optional emphasis hint: e.g. 'show_result', 'show_decline', "
            "'show_scale', 'highlight_risk'."
        ),
    )
    trigger_word: str | None = Field(
        default=None,
        description=(
            "A single verbatim word from the narration that triggers this visual switch. "
            "Must be null for the first intent of an idea. "
            "Must appear verbatim in narration_excerpt."
        ),
    )

    @field_validator("relationship_type")
    @classmethod
    def relationship_type_must_be_valid(cls, value: str) -> str:
        if value not in VALID_RELATIONSHIP_TYPES:
            raise ValueError(
                f"relationship_type '{value}' is not allowed. "
                f"Must be one of: {', '.join(VALID_RELATIONSHIP_TYPES)}"
            )
        return value


class VisualIntentSequence(BaseModel):
    """
    The ordered sequence of VisualIntents for one narrative idea.
    Output of VisualIntentEngine.run() for a single idea.
    """

    schema_version: str = "1"
    idea_id: str = Field(description="Matches the idea_id from ScriptVisualStrategy.ideas.")
    narration: str = Field(description="The full narration text this sequence covers.")
    intents: list[VisualIntent] = Field(
        description=(
            "Ordered visual intents. May be empty if narration "
            "contains only filler/transitions."
        )
    )
