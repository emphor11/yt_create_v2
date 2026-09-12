"""
Composition Plan domain models.

A CompositionPlan represents the output of the CompositionPlannerEngine:
for each VisualIntent, the planner has selected a registered composition
and populated its data schema.

This is stored inside the script_visual_strategy artifact payload when
visual_mode == "composition".
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompositionBeat(BaseModel):
    """
    A single visual beat in the composition pipeline.

    Analogous to VisualStrategyBeat in the legacy system, but operates at the
    composition level (what storytelling pattern) rather than component level
    (which React component).
    """

    beat_id: str = Field(description="Sequential: beat_01, beat_02, ...")
    composition_id: str = Field(
        description="A registered composition ID from CompositionRegistry. "
                    "e.g. 'metric_hero', 'calculation_story', 'broll_caption'."
    )
    variant: str | None = Field(
        default=None,
        description="Optional composition-specific variant. Must be in composition's allowed_variants.",
    )
    composition_data: dict[str, Any] = Field(
        default_factory=dict,
        description="Data payload validated against the composition's Pydantic data model.",
    )
    asset_requirement: str = Field(
        default="none",
        description="'none' | 'optional_broll' | 'required_image'",
    )
    asset_query: str | None = Field(
        default=None,
        description="Stock media search query string if asset_requirement != 'none'.",
    )
    trigger_word: str | None = Field(
        default=None,
        description=(
            "A single verbatim word from the narration that triggers this beat. "
            "Same verbatim-matching rules as the legacy system."
        ),
    )
    visual_goal: str = Field(
        default="",
        description="Human-readable description of visual intent. Kept for debugging/logging only.",
    )
    relationship_type: str | None = Field(
        default=None,
        description="The semantic relationship_type from VisualIntent this beat was created for.",
    )
    used_fallback: bool = Field(
        default=False,
        description="True if this beat was created as a fallback rather than primary planner selection.",
    )
    fallback_reason: str | None = Field(
        default=None,
        description="Detailed reason if this beat was created via fallback (e.g. 'no_suitable_composition', 'validation_error').",
    )


class IdeaCompositionPlan(BaseModel):
    """Composition beats for one narrative idea."""

    idea_id: str
    narration: str
    beats: list[CompositionBeat] = Field(default_factory=list)


class FullCompositionPlan(BaseModel):
    """
    Complete composition plan for an entire video.

    This is attached to the script_visual_strategy artifact payload under
    the key "composition_plan" when visual_mode == "composition".
    """

    schema_version: str = "1"
    visual_mode: str = "composition"  # detector flag for VideoAssemblyHandler
    thesis: str
    ideas: list[IdeaCompositionPlan] = Field(default_factory=list)
