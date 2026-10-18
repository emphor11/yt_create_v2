from __future__ import annotations

import pytest

from domain.continuous_story_plan import ContinuousStoryPlanArtifact
from domain.validators.continuous_story_plan_validator import ContinuousStoryPlanValidator


@pytest.fixture
def valid_plan_dict() -> dict:
    return {
        "id": "loan_rate_hike",
        "fps": 30,
        "durationInFrames": 505,
        "width": 1920,
        "height": 1080,
        "safeMargin": 80,
        "audioFileName": "loan_narration.mp3",
        "narration": {
            "text": "A 50 lakh home loan...",
            "audioFile": "loan_narration.mp3",
            "wordTimestamps": [{"word": "A", "start_ms": 0, "end_ms": 300}],
        },
        "objects": [
            {"id": "loan_card", "type": "card", "layout": "center", "children": []}
        ],
        "events": [
            {"action": "enter", "targetId": "loan_card", "startFrame": 10, "durationFrames": 25}
        ],
    }


@pytest.fixture
def valid_artifact(valid_plan_dict: dict) -> ContinuousStoryPlanArtifact:
    return ContinuousStoryPlanArtifact.from_compiled_plan(
        plan=valid_plan_dict,
        audio_storage_key="projects/p1/runs/r1/loan_narration.mp3",
    )


def test_validator_accepts_valid_artifact(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    result = validator.validate(valid_artifact)
    assert result.status == "valid"
    assert len(result.errors) == 0


def test_validator_rejects_story_id_mismatch(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    # Mutate plan ID to create mismatch
    valid_artifact.plan["id"] = "different_story_id"
    result = validator.validate(valid_artifact)
    assert result.status == "failed"
    assert any("story_id" in err for err in result.errors)


def test_validator_rejects_duration_mismatch(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    valid_artifact.plan["durationInFrames"] = 999
    result = validator.validate(valid_artifact)
    assert result.status == "failed"
    assert any("duration" in err for err in result.errors)


def test_validator_rejects_empty_objects(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    valid_artifact.plan["objects"] = []
    result = validator.validate(valid_artifact)
    assert result.status == "failed"
    assert any("objects" in err for err in result.errors)


def test_validator_rejects_empty_events(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    valid_artifact.plan["events"] = []
    result = validator.validate(valid_artifact)
    assert result.status == "failed"
    assert any("events" in err for err in result.errors)


def test_validator_storage_key_enforcement(valid_artifact: ContinuousStoryPlanArtifact):
    validator = ContinuousStoryPlanValidator()
    # With storage key present, require_storage_key=True should pass
    result_with_key = validator.validate(valid_artifact, require_storage_key=True)
    assert result_with_key.status == "valid"

    # With storage key missing, require_storage_key=True should fail
    valid_artifact.audio_storage_key = None
    result_without_key = validator.validate(valid_artifact, require_storage_key=True)
    assert result_without_key.status == "failed"
    assert any("audio_storage_key" in err for err in result_without_key.errors)
