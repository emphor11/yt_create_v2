"""
CompositionSelector — pure deterministic routing from VisualIntent to composition_id.

Principles:
- Pure Python, zero LLM calls.
- Maps semantic relationship types to authoritative composition IDs.
- Deterministic disambiguation guards for multi-target relationships (comparison, trend).
- Fail-fast: raises CompositionSelectionError when selection is ambiguous, incomplete, or unsupported.
- Never repairs missing semantic data.
- Never uses B-roll as a fallback for invalid or ambiguous data.
"""
from __future__ import annotations

from domain.visual_intent import VisualIntent


class CompositionSelectionError(Exception):
    """Raised when deterministic composition selection cannot be made."""

    def __init__(self, relationship_type: str, reason: str):
        super().__init__(f"Cannot select composition for relationship_type '{relationship_type}': {reason}")
        self.relationship_type = relationship_type
        self.reason = reason


PRIMARY_RELATIONSHIP_MAP: dict[str, str] = {
    "metric": "metric_hero",
    "calculation": "calculation_story",
    "cause_effect": "cause_effect",
    "multi_factor": "multi_factor_pressure",
    "ranking": "ranked_list",
    "process": "process_flow",
    "decline": "time_decay",
    "growth": "growth_trajectory",
    "waterfall": "cash_flow_waterfall",
    "statement": "broll_caption",
    "quote": "broll_caption",
    "definition": "broll_caption",
    "broll": "broll_caption",
    "comparison": "comparison_split",
    "divergence": "trajectory_divergence",
}


def select_composition_for_intent(intent: VisualIntent) -> str:
    """
    Deterministically selects the authoritative composition_id for a given VisualIntent.
    Fails fast with CompositionSelectionError if selection is ambiguous, incomplete, or unsupported.

    Returns:
        composition_id (str)

    Raises:
        CompositionSelectionError: If relationship is unsupported or required disambiguation data is absent.
    """
    rel_type = intent.relationship_type

    # 'trend' is deprecated in favor of explicit 'growth' and 'decline'.
    # For backward compatibility with existing artifacts, resolve trend deterministically:
    if rel_type == "trend":
        has_decay = bool(intent.temporal and intent.temporal.is_decay_over_time)
        downward_measurement = any(m.direction == "down" for m in intent.measurements)
        upward_measurement = any(m.direction == "up" for m in intent.measurements)

        if has_decay or downward_measurement:
            if upward_measurement:
                raise CompositionSelectionError(
                    rel_type,
                    "trend contains contradictory directions (both upward and downward measurements).",
                )
            return "time_decay"

        # If not downward, resolve to growth_trajectory
        return "growth_trajectory"

    # 3. Direct Primary Mappings
    if rel_type in PRIMARY_RELATIONSHIP_MAP:
        return PRIMARY_RELATIONSHIP_MAP[rel_type]

    # 4. Unsupported or unmapped relationship types (e.g. amortization, accumulation)
    raise CompositionSelectionError(
        rel_type,
        f"relationship_type '{rel_type}' is unsupported or has no registered composition.",
    )
