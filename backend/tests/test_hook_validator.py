from domain.hook import Hook, VisualDirective
from domain.validators.hook_validator import HookValidator


def test_validator_accepts_valid_hook() -> None:
    hook = Hook(
        conceptual_hook="Anchor vs Engine comparison",
        script_text="Are you renting? You might think you're throwing money away. You're not.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="Show heavy metal anchor falling in water", onscreen_text="RENTING = WASTED MONEY?", trigger_word=None),
            VisualDirective(beat_id="beat_02", visual_instruction="Show rocket engine firing upward", onscreen_text="THE LIQUID ENGINE", trigger_word="throwing"),
        ],
    )
    result = HookValidator().validate(hook)
    assert result.status == "valid"
    assert not result.errors


def test_validator_rejects_insufficient_visual_directives() -> None:
    hook = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="Only one visual instruction beat")
        ],
    )
    result = HookValidator().validate(hook)
    assert result.status == "blocked"
    assert "must contain at least 2 visual directives" in result.errors[0]


def test_validator_rejects_invalid_trigger_word() -> None:
    # 1. Missing trigger word for subsequent directive
    hook_missing = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script here.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="First beat"),
            VisualDirective(beat_id="beat_02", visual_instruction="Second beat"),
        ],
    )
    result = HookValidator().validate(hook_missing)
    assert result.status == "blocked"
    assert "is a subsequent beat and requires trigger_word" in result.errors[0]

    # 2. Trigger word not in hook script text
    hook_mismatch = Hook(
        conceptual_hook="Concept Description",
        script_text="Intro spoken script here.",
        visual_directives=[
            VisualDirective(beat_id="beat_01", visual_instruction="First beat"),
            VisualDirective(beat_id="beat_02", visual_instruction="Second beat", trigger_word="nonexistent"),
        ],
    )
    result_err = HookValidator().validate(hook_mismatch)
    assert result_err.status == "blocked"
    assert "does not exist in the script text" in result_err.errors[0]

