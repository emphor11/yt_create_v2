"""Persisted VisualIntent artifact and source provenance models."""
from __future__ import annotations

import hashlib
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from domain.visual_intent import VisualIntentSequence


class VisualIntentProvenance(BaseModel):
    """Source location for one intent inside its narration section."""

    model_config = ConfigDict(extra="forbid")

    idea_id: str
    intent_id: str
    source_kind: Literal["hook", "idea"]
    source_id: str
    source_text_sha256: str
    excerpt_start: int = Field(ge=0)
    excerpt_end: int = Field(gt=0)


class VisualIntentArtifact(BaseModel):
    """The inspectable, run-scoped source of truth for composition planning."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    sequences: list[VisualIntentSequence] = Field(default_factory=list)
    provenance: list[VisualIntentProvenance] = Field(default_factory=list)
    provider_metadata: list[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_provenance(self) -> "VisualIntentArtifact":
        if len({sequence.idea_id for sequence in self.sequences}) != len(self.sequences):
            raise ValueError("VisualIntent artifact cannot contain duplicate idea_id sequences.")

        sequence_by_idea = {sequence.idea_id: sequence for sequence in self.sequences}
        expected_keys = {
            (sequence.idea_id, intent.intent_id)
            for sequence in self.sequences
            for intent in sequence.intents
        }
        actual_keys = {(item.idea_id, item.intent_id) for item in self.provenance}

        if expected_keys != actual_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)
            raise ValueError(
                f"VisualIntent provenance must cover each intent exactly once; "
                f"missing={missing}, extra={extra}."
            )

        for item in self.provenance:
            sequence = sequence_by_idea.get(item.idea_id)
            if sequence is None:
                raise ValueError(f"Unknown provenance idea_id '{item.idea_id}'.")
            intent = next(
                (candidate for candidate in sequence.intents if candidate.intent_id == item.intent_id),
                None,
            )
            if intent is None:
                raise ValueError(
                    f"Unknown provenance intent_id '{item.intent_id}' for idea '{item.idea_id}'."
                )

            source_text = sequence.narration
            if item.source_id != item.idea_id:
                raise ValueError(
                    f"Provenance source_id '{item.source_id}' must match idea_id '{item.idea_id}'."
                )
            if item.source_kind == "hook" and item.idea_id != "hook":
                raise ValueError("Only the 'hook' sequence may use source_kind='hook'.")
            if item.source_kind == "idea" and item.idea_id == "hook":
                raise ValueError("The 'hook' sequence must use source_kind='hook'.")
            if item.excerpt_end > len(source_text):
                raise ValueError(
                    f"Provenance span for '{item.idea_id}/{item.intent_id}' exceeds source text."
                )
            if source_text[item.excerpt_start:item.excerpt_end] != intent.narration_excerpt:
                raise ValueError(
                    f"Provenance span for '{item.idea_id}/{item.intent_id}' does not match "
                    "the verbatim narration_excerpt."
                )
            if hashlib.sha256(source_text.encode("utf-8")).hexdigest() != item.source_text_sha256:
                raise ValueError(
                    f"Provenance source hash for '{item.idea_id}/{item.intent_id}' does not match narration."
                )

        return self


def build_visual_intent_provenance(
    sequence: VisualIntentSequence,
    *,
    source_kind: Literal["hook", "idea"],
) -> list[VisualIntentProvenance]:
    """Build source spans from the engine-validated ordered excerpts."""

    source_text = sequence.narration
    source_hash = hashlib.sha256(source_text.encode("utf-8")).hexdigest()
    cursor = 0
    records: list[VisualIntentProvenance] = []

    for intent in sequence.intents:
        start = source_text.find(intent.narration_excerpt, cursor)
        if start < 0:
            raise ValueError(
                f"Intent '{sequence.idea_id}/{intent.intent_id}' is not a verbatim span "
                "of its source narration."
            )
        end = start + len(intent.narration_excerpt)
        records.append(
            VisualIntentProvenance(
                idea_id=sequence.idea_id,
                intent_id=intent.intent_id,
                source_kind=source_kind,
                source_id=sequence.idea_id,
                source_text_sha256=source_hash,
                excerpt_start=start,
                excerpt_end=end,
            )
        )
        cursor = end

    return records
