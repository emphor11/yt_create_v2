from __future__ import annotations

from typing import Any
from domain.continuous_story_plan import ContinuousStoryPlanArtifact
from domain.validation import ValidationResult


class ContinuousStoryPlanValidator:
    """
    Artifact-level validator for ContinuousStoryPlanArtifact.

    Verifies top-level artifact metadata, consistency between the artifact envelope
    and the compiled StoryPlan payload, and existence of required render objects.
    Draft-level validation and Remotion scene validation are handled by their own layers.
    """

    def validate(
        self,
        artifact: ContinuousStoryPlanArtifact,
        *,
        require_storage_key: bool = False,
    ) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        # 1. Top-level parameter positivity & string presence
        if not artifact.story_id or not artifact.story_id.strip():
            errors.append("ContinuousStoryPlanArtifact story_id must be a non-empty string.")

        if artifact.fps <= 0:
            errors.append(f"ContinuousStoryPlanArtifact fps must be positive, got {artifact.fps}.")

        if artifact.duration_in_frames <= 0:
            errors.append(
                f"ContinuousStoryPlanArtifact duration_in_frames must be positive, got {artifact.duration_in_frames}."
            )

        if artifact.width <= 0:
            errors.append(f"ContinuousStoryPlanArtifact width must be positive, got {artifact.width}.")

        if artifact.height <= 0:
            errors.append(f"ContinuousStoryPlanArtifact height must be positive, got {artifact.height}.")

        if not artifact.audio_file_name or not artifact.audio_file_name.strip():
            errors.append("ContinuousStoryPlanArtifact audio_file_name must be a non-empty string.")

        # 2. Audio storage key check (if production storage is required)
        if require_storage_key and (not artifact.audio_storage_key or not artifact.audio_storage_key.strip()):
            errors.append("ContinuousStoryPlanArtifact audio_storage_key is required when storage persistence is enabled.")

        # 3. Plan dictionary presence
        plan = artifact.plan
        if not isinstance(plan, dict) or not plan:
            errors.append("ContinuousStoryPlanArtifact plan must be a non-empty dictionary.")
            return ValidationResult(status="failed", errors=errors, warnings=warnings)

        # 4. Consistency between artifact envelope and plan payload
        plan_id = plan.get("id") or plan.get("story_id")
        if plan_id != artifact.story_id:
            errors.append(
                f"Artifact story_id ('{artifact.story_id}') does not match plan id ('{plan_id}')."
            )

        plan_duration = plan.get("durationInFrames") or plan.get("duration_in_frames")
        if plan_duration is not None and plan_duration != artifact.duration_in_frames:
            errors.append(
                f"Artifact duration_in_frames ({artifact.duration_in_frames}) does not match plan duration ({plan_duration})."
            )

        plan_fps = plan.get("fps")
        if plan_fps is not None and plan_fps != artifact.fps:
            errors.append(
                f"Artifact fps ({artifact.fps}) does not match plan fps ({plan_fps})."
            )

        plan_width = plan.get("width")
        if plan_width is not None and plan_width != artifact.width:
            errors.append(
                f"Artifact width ({artifact.width}) does not match plan width ({plan_width})."
            )

        plan_height = plan.get("height")
        if plan_height is not None and plan_height != artifact.height:
            errors.append(
                f"Artifact height ({artifact.height}) does not match plan height ({plan_height})."
            )

        plan_audio = plan.get("audioFileName") or plan.get("audio_file_name")
        if plan_audio and plan_audio != artifact.audio_file_name:
            errors.append(
                f"Artifact audio_file_name ('{artifact.audio_file_name}') does not match plan audio ('{plan_audio}')."
            )

        # 5. Core rendering collections
        objects = plan.get("objects")
        if not isinstance(objects, list) or len(objects) == 0:
            errors.append("Compiled plan must contain a non-empty list of 'objects'.")

        events = plan.get("events")
        if not isinstance(events, list) or len(events) == 0:
            errors.append("Compiled plan must contain a non-empty list of 'events'.")

        if errors:
            return ValidationResult(status="failed", errors=errors, warnings=warnings)
        if warnings:
            return ValidationResult(status="warning", errors=errors, warnings=warnings)
        return ValidationResult(status="valid", errors=[], warnings=[])
